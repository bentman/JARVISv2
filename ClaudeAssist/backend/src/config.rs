use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub database: DatabaseConfig,
    pub ollama: OllamaConfig,
    pub models: ModelsConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OllamaConfig {
    pub base_url: String,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelsConfig {
    pub light_tier: Vec<String>,
    pub medium_tier: Vec<String>,
    pub heavy_tier: Vec<String>,
    pub npu_tier: Vec<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            database: DatabaseConfig {
                path: "data/assistant.db".to_string(),
            },
            ollama: OllamaConfig {
                base_url: "http://localhost:11434".to_string(),
                timeout_seconds: 300,
            },
            models: ModelsConfig {
                light_tier: vec!["phi3:3.8b".to_string()],
                medium_tier: vec!["gemma2:9b".to_string(), "deepseek-coder:6.7b".to_string()],
                heavy_tier: vec![
                    "llama3.1:8b".to_string(),
                    "gemma2:27b".to_string(),
                    "deepseek-coder:33b".to_string(),
                ],
                npu_tier: vec!["phi3:3.8b".to_string(), "gemma2:2b".to_string()],
            },
        }
    }
}

impl Config {
    pub async fn load<P: AsRef<Path>>(path: P) -> Result<Self> {
        if path.as_ref().exists() {
            let content = tokio::fs::read_to_string(path).await?;
            let config: Config = serde_yaml::from_str(&content)?;
            Ok(config)
        } else {
            // Create default config if file doesn't exist
            let config = Config::default();
            let content = serde_yaml::to_string(&config)?;
            if let Some(parent) = path.as_ref().parent() {
                tokio::fs::create_dir_all(parent).await?;
            }
            tokio::fs::write(path, content).await?;
            Ok(config)
        }
    }
}

// Add serde_yaml dependency to Cargo.toml
// serde_yaml = "0.9"