use anyhow::Result;
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use clap::Parser;
use serde::{Deserialize, Serialize};
use std::{net::SocketAddr, sync::Arc};
use tower_http::cors::CorsLayer;
use tracing::{info, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod config;
mod database;
mod hardware;
mod models;
mod ollama;

use config::Config;
use database::Database;
use hardware::{HardwareDetector, HardwareTier};
use models::{ChatMessage, ChatRequest, ChatResponse, MemoryEntry, SearchRequest, SearchResponse};

#[derive(Parser)]
#[command(name = "ai-assistant-backend")]
#[command(about = "Local-first AI Assistant Backend")]
struct Cli {
    #[arg(short, long, default_value = "0.0.0.0:8080")]
    bind: SocketAddr,
    
    #[arg(short, long, default_value = "config.yaml")]
    config: String,
}

#[derive(Clone)]
struct AppState {
    database: Database,
    hardware_detector: Arc<HardwareDetector>,
    ollama_client: ollama::Client,
    config: Config,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let cli = Cli::parse();
    
    // Load configuration
    let config = Config::load(&cli.config).await?;
    info!("Loaded configuration from {}", cli.config);

    // Initialize hardware detector
    let hardware_detector = Arc::new(HardwareDetector::new());
    let hardware_tier = hardware_detector.detect_tier();
    info!("Detected hardware tier: {:?}", hardware_tier);

    // Initialize database
    let database = Database::new(&config.database.path).await?;
    info!("Initialized database");

    // Initialize Ollama client
    let ollama_client = ollama::Client::new(&config.ollama.base_url);
    
    // Setup models based on hardware tier
    setup_models(&ollama_client, hardware_tier).await?;

    let state = AppState {
        database,
        hardware_detector,
        ollama_client,
        config,
    };

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/hardware", get(get_hardware_info))
        .route("/chat", post(chat_handler))
        .route("/memory", get(get_memory).post(save_memory))
        .route("/memory/:id", get(get_memory_by_id))
        .route("/search", post(search_handler))
        .layer(CorsLayer::permissive())
        .with_state(state);

    info!("Starting server on {}", cli.bind);
    let listener = tokio::net::TcpListener::bind(cli.bind).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn setup_models(ollama_client: &ollama::Client, hardware_tier: HardwareTier) -> Result<()> {
    let models = match hardware_tier {
        HardwareTier::Light => vec!["phi3:3.8b"],
        HardwareTier::Medium => vec!["gemma2:9b", "deepseek-coder:6.7b"],
        HardwareTier::Heavy => vec!["llama3.1:8b", "gemma2:27b", "deepseek-coder:33b"],
        HardwareTier::NPU => vec!["phi3:3.8b", "gemma2:2b"],
    };

    info!("Setting up models for {:?}: {:?}", hardware_tier, models);
    
    for model in models {
        match ollama_client.pull_model(model).await {
            Ok(_) => info!("Successfully pulled model: {}", model),
            Err(e) => warn!("Failed to pull model {}: {}", model, e),
        }
    }

    Ok(())
}

async fn health_check() -> &'static str {
    "OK"
}

async fn get_hardware_info(State(state): State<AppState>) -> Json<serde_json::Value> {
    let tier = state.hardware_detector.detect_tier();
    let info = state.hardware_detector.get_detailed_info();
    
    Json(serde_json::json!({
        "tier": format!("{:?}", tier),
        "details": info
    }))
}

async fn chat_handler(
    State(state): State<AppState>,
    Json(request): Json<ChatRequest>,
) -> Result<Json<ChatResponse>, StatusCode> {
    let hardware_tier = state.hardware_detector.detect_tier();
    
    // Select appropriate model based on request type and hardware
    let model = select_model_for_request(&request, hardware_tier);
    
    // Route to appropriate handler
    let response_text = match request.message_type.as_deref() {
        Some("code") => handle_coding_request(&state.ollama_client, &model, &request).await,
        Some("reasoning") => handle_reasoning_request(&state.ollama_client, &model, &request).await,
        _ => handle_chat_request(&state.ollama_client, &model, &request).await,
    };

    match response_text {
        Ok(text) => {
            // Save to memory
            let memory_entry = MemoryEntry {
                id: uuid::Uuid::new_v4().to_string(),
                message: request.message.clone(),
                response: text.clone(),
                timestamp: chrono::Utc::now(),
                message_type: request.message_type.clone(),
            };
            
            if let Err(e) = state.database.save_memory(&memory_entry).await {
                warn!("Failed to save memory: {}", e);
            }

            Ok(Json(ChatResponse {
                response: text,
                model_used: model,
            }))
        }
        Err(e) => {
            warn!("Chat request failed: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

fn select_model_for_request(request: &ChatRequest, tier: HardwareTier) -> String {
    match (request.message_type.as_deref(), tier) {
        (Some("code"), HardwareTier::Heavy) => "deepseek-coder:33b".to_string(),
        (Some("code"), HardwareTier::Medium) => "deepseek-coder:6.7b".to_string(),
        (Some("code"), _) => "phi3:3.8b".to_string(),
        
        (Some("reasoning"), HardwareTier::Heavy) => "llama3.1:8b".to_string(),
        (Some("reasoning"), HardwareTier::Medium) => "gemma2:9b".to_string(),
        (Some("reasoning"), _) => "phi3:3.8b".to_string(),
        
        (_, HardwareTier::Heavy) => "llama3.1:8b".to_string(),
        (_, HardwareTier::Medium) => "gemma2:9b".to_string(),
        (_, HardwareTier::NPU) => "gemma2:2b".to_string(),
        (_, HardwareTier::Light) => "phi3:3.8b".to_string(),
    }
}

async fn handle_chat_request(
    ollama_client: &ollama::Client,
    model: &str,
    request: &ChatRequest,
) -> Result<String> {
    let system_prompt = "You are a helpful AI assistant. Provide clear, concise, and accurate responses.";
    ollama_client.generate(model, system_prompt, &request.message).await
}

async fn handle_reasoning_request(
    ollama_client: &ollama::Client,
    model: &str,
    request: &ChatRequest,
) -> Result<String> {
    let system_prompt = "You are an AI assistant specialized in logical reasoning and problem-solving. Break down complex problems step by step and provide detailed analysis.";
    ollama_client.generate(model, system_prompt, &request.message).await
}

async fn handle_coding_request(
    ollama_client: &ollama::Client,
    model: &str,
    request: &ChatRequest,
) -> Result<String> {
    let system_prompt = "You are an expert programming assistant. Provide clean, well-documented code with explanations. Consider best practices, error handling, and performance.";
    ollama_client.generate(model, system_prompt, &request.message).await
}

#[derive(Deserialize)]
struct MemoryQuery {
    limit: Option<u32>,
    offset: Option<u32>,
}

async fn get_memory(
    State(state): State<AppState>,
    Query(query): Query<MemoryQuery>,
) -> Result<Json<Vec<MemoryEntry>>, StatusCode> {
    let limit = query.limit.unwrap_or(50);
    let offset = query.offset.unwrap_or(0);
    
    match state.database.get_memory(limit, offset).await {
        Ok(entries) => Ok(Json(entries)),
        Err(e) => {
            warn!("Failed to get memory: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn get_memory_by_id(
    State(state): State<AppState>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> Result<Json<MemoryEntry>, StatusCode> {
    match state.database.get_memory_by_id(&id).await {
        Ok(Some(entry)) => Ok(Json(entry)),
        Ok(None) => Err(StatusCode::NOT_FOUND),
        Err(e) => {
            warn!("Failed to get memory by id: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn save_memory(
    State(state): State<AppState>,
    Json(entry): Json<MemoryEntry>,
) -> Result<Json<MemoryEntry>, StatusCode> {
    match state.database.save_memory(&entry).await {
        Ok(_) => Ok(Json(entry)),
        Err(e) => {
            warn!("Failed to save memory: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn search_handler(
    State(_state): State<AppState>,
    Json(request): Json<SearchRequest>,
) -> Result<Json<SearchResponse>, StatusCode> {
    // This is a stub implementation for local search
    // In a full implementation, this would use vector embeddings
    // and semantic search through stored conversations
    
    Ok(Json(SearchResponse {
        results: vec![],
        query: request.query,
        total_results: 0,
    }))
}