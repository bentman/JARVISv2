use anyhow::{anyhow, Result};
use reqwest::Client as HttpClient;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::time::Duration;
use tracing::{info, warn};

#[derive(Clone)]
pub struct Client {
    http_client: HttpClient,
    base_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct GenerateRequest {
    model: String,
    prompt: String,
    stream: bool,
    options: Option<GenerateOptions>,
}

#[derive(Debug, Serialize, Deserialize)]
struct GenerateOptions {
    temperature: Option<f64>,
    top_k: Option<i32>,
    top_p: Option<f64>,
    num_predict: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct GenerateResponse {
    model: String,
    created_at: String,
    response: String,
    done: bool,
    context: Option<Vec<i32>>,
    total_duration: Option<u64>,
    load_duration: Option<u64>,
    prompt_eval_count: Option<i32>,
    prompt_eval_duration: Option<u64>,
    eval_count: Option<i32>,
    eval_duration: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PullRequest {
    name: String,
    stream: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct PullResponse {
    status: String,
    digest: Option<String>,
    total: Option<u64>,
    completed: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ListResponse {
    models: Vec<ModelInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ModelInfo {
    name: String,
    modified_at: String,
    size: u64,
    digest: String,
    details: ModelDetails,
}

#[derive(Debug, Serialize, Deserialize)]
struct ModelDetails {
    format: String,
    family: String,
    families: Option<Vec<String>>,
    parameter_size: String,
    quantization_level: String,
}

impl Client {
    pub fn new(base_url: &str) -> Self {
        let http_client = HttpClient::builder()
            .timeout(Duration::from_secs(300))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            http_client,
            base_url: base_url.to_string(),
        }
    }

    pub async fn generate(&self, model: &str, system_prompt: &str, user_message: &str) -> Result<String> {
        let full_prompt = format!("System: {}\n\nHuman: {}\n\nAssistant:", system_prompt, user_message);
        
        let request = GenerateRequest {
            model: model.to_string(),
            prompt: full_prompt,
            stream: false,
            options: Some(GenerateOptions {
                temperature: Some(0.7),
                top_k: Some(40),
                top_p: Some(0.9),
                num_predict: Some(2048),
            }),
        };

        let url = format!("{}/api/generate", self.base_url);
        let response = self.http_client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            return Err(anyhow!("Ollama API error: {}", error_text));
        }

        let generate_response: GenerateResponse = response.json().await?;
        Ok(generate_response.response)
    }

    pub async fn pull_model(&self, model_name: &str) -> Result<()> {
        info!("Pulling model: {}", model_name);
        
        let request = PullRequest {
            name: model_name.to_string(),
            stream: false,
        };

        let url = format!("{}/api/pull", self.base_url);
        let response = self.http_client
            .post(&url)
            .json(&request)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            return Err(anyhow!("Failed to pull model {}: {}", model_name, error_text));
        }

        let pull_response: PullResponse = response.json().await?;
        
        match pull_response.status.as_str() {
            "success" => {
                info!("Successfully pulled model: {}", model_name);
                Ok(())
            }
            status => {
                warn!("Model pull status: {} for {}", status, model_name);
                Ok(()) // Don't fail on warning statuses
            }
        }
    }

    pub async fn list_models(&self) -> Result<Vec<String>> {
        let url = format!("{}/api/tags", self.base_url);
        let response = self.http_client
            .get(&url)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            return Err(anyhow!("Failed to list models: {}", error_text));
        }

        let list_response: ListResponse = response.json().await?;
        Ok(list_response.models.into_iter().map(|m| m.name).collect())
    }

    pub async fn is_model_available(&self, model_name: &str) -> bool {
        match self.list_models().await {
            Ok(models) => models.iter().any(|m| m.starts_with(model_name)),
            Err(e) => {
                warn!("Failed to check model availability: {}", e);
                false
            }
        }
    }

    pub async fn health_check(&self) -> Result<()> {
        let url = format!("{}/api/tags", self.base_url);
        let response = self.http_client
            .get(&url)
            .timeout(Duration::from_secs(5))
            .send()
            .await?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(anyhow!("Ollama health check failed"))
        }
    }
}