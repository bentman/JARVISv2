use anyhow::Result;
use sqlx::{sqlite::SqlitePool, Row, Sqlite, Pool};
use crate::models::MemoryEntry;

#[derive(Clone)]
pub struct Database {
    pool: Pool<Sqlite>,
}

impl Database {
    pub async fn new(database_path: &str) -> Result<Self> {
        // Ensure the parent directory exists
        if let Some(parent) = std::path::Path::new(database_path).parent() {
            tokio::fs::create_dir_all(parent).await?;
        }

        let pool = SqlitePool::connect(&format!("sqlite:{}", database_path)).await?;
        
        // Run migrations
        Self::migrate(&pool).await?;
        
        Ok(Self { pool })
    }
    
    async fn migrate(pool: &Pool<Sqlite>) -> Result<()> {
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                message_type TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory(timestamp);
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memory(message_type);
            "#,
        )
        .execute(pool)
        .await?;
        
        Ok(())
    }
    
    pub async fn save_memory(&self, entry: &MemoryEntry) -> Result<()> {
        sqlx::query(
            "INSERT OR REPLACE INTO memory (id, message, response, timestamp, message_type) VALUES (?, ?, ?, ?, ?)"
        )
        .bind(&entry.id)
        .bind(&entry.message)
        .bind(&entry.response)
        .bind(&entry.timestamp)
        .bind(&entry.message_type)
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    pub async fn get_memory(&self, limit: u32, offset: u32) -> Result<Vec<MemoryEntry>> {
        let rows = sqlx::query(
            "SELECT id, message, response, timestamp, message_type FROM memory ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        )
        .bind(limit)
        .bind(offset)
        .fetch_all(&self.pool)
        .await?;
        
        let mut entries = Vec::new();
        for row in rows {
            entries.push(MemoryEntry {
                id: row.get("id"),
                message: row.get("message"),
                response: row.get("response"),
                timestamp: row.get("timestamp"),
                message_type: row.get("message_type"),
            });
        }
        
        Ok(entries)
    }
    
    pub async fn get_memory_by_id(&self, id: &str) -> Result<Option<MemoryEntry>> {
        let row = sqlx::query(
            "SELECT id, message, response, timestamp, message_type FROM memory WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(&self.pool)
        .await?;
        
        if let Some(row) = row {
            Ok(Some(MemoryEntry {
                id: row.get("id"),
                message: row.get("message"),
                response: row.get("response"),
                timestamp: row.get("timestamp"),
                message_type: row.get("message_type"),
            }))
        } else {
            Ok(None)
        }
    }
    
    pub async fn search_memory(&self, query: &str, limit: u32) -> Result<Vec<MemoryEntry>> {
        let rows = sqlx::query(
            r#"
            SELECT id, message, response, timestamp, message_type 
            FROM memory 
            WHERE message LIKE ? OR response LIKE ?
            ORDER BY timestamp DESC 
            LIMIT ?
            "#
        )
        .bind(format!("%{}%", query))
        .bind(format!("%{}%", query))
        .bind(limit)
        .fetch_all(&self.pool)
        .await?;
        
        let mut entries = Vec::new();
        for row in rows {
            entries.push(MemoryEntry {
                id: row.get("id"),
                message: row.get("message"),
                response: row.get("response"),
                timestamp: row.get("timestamp"),
                message_type: row.get("message_type"),
            });
        }
        
        Ok(entries)
    }
}