use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareInfo {
    pub cpu_info: CpuInfo,
    pub memory_info: MemoryInfo,
    pub gpu_info: Vec<GpuInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuInfo {
    pub brand: String,
    pub cores: usize,
    pub threads: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryInfo {
    pub total_gb: f64,
    pub available_gb: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuInfo {
    pub name: String,
    pub vendor: String,
    pub memory_gb: Option<f64>,
}

pub struct HardwareDetector;

impl HardwareDetector {
    pub fn new() -> Self {
        Self
    }

    pub fn get_hardware_info(&self) -> HardwareInfo {
        // This is a simplified implementation
        // In a real application, you'd use system APIs or crates like `sysinfo`
        // to get actual hardware information
        
        HardwareInfo {
            cpu_info: CpuInfo {
                brand: "Unknown CPU".to_string(),
                cores: num_cpus::get(),
                threads: num_cpus::get(),
            },
            memory_info: MemoryInfo {
                total_gb: 16.0, // Placeholder
                available_gb: 8.0, // Placeholder
            },
            gpu_info: vec![
                GpuInfo {
                    name: "Integrated Graphics".to_string(),
                    vendor: "Unknown".to_string(),
                    memory_gb: None,
                }
            ],
        }
    }
}