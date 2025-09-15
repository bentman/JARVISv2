use serde::{Deserialize, Serialize};
use sysinfo::{System, SystemExt, ComponentExt};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum HardwareTier {
    Light,   // CPU only, <16GB RAM
    Medium,  // GPU 4-8GB VRAM, or 16-32GB RAM
    Heavy,   // GPU >8GB VRAM, or >32GB RAM
    NPU,     // Neural Processing Unit detected
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareInfo {
    pub total_memory_gb: f64,
    pub cpu_count: usize,
    pub cpu_brand: String,
    pub gpu_info: Vec<GpuInfo>,
    pub npu_detected: bool,
    pub os_info: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuInfo {
    pub name: String,
    pub vram_gb: Option<f64>,
    pub vendor: String,
}

pub struct HardwareDetector {
    system: System,
}

impl HardwareDetector {
    pub fn new() -> Self {
        let mut system = System::new_all();
        system.refresh_all();
        Self { system }
    }
    
    pub fn detect_tier(&self) -> HardwareTier {
        let hardware_info = self.get_detailed_info();
        
        // Check for NPU first
        if hardware_info.npu_detected {
            return HardwareTier::NPU;
        }
        
        // Check GPU VRAM
        let max_vram = hardware_info.gpu_info
            .iter()
            .filter_map(|gpu| gpu.vram_gb)
            .max_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or(0.0);
        
        if max_vram > 8.0 {
            return HardwareTier::Heavy;
        }
        
        if max_vram >= 4.0 {
            return HardwareTier::Medium;
        }
        
        // Fallback to RAM-based classification
        let total_ram_gb = hardware_info.total_memory_gb;
        
        if total_ram_gb > 32.0 {
            HardwareTier::Heavy
        } else if total_ram_gb >= 16.0 {
            HardwareTier::Medium
        } else {
            HardwareTier::Light
        }
    }
    
    pub fn get_detailed_info(&self) -> HardwareInfo {
        let total_memory_gb = self.system.total_memory() as f64 / (1024.0 * 1024.0 * 1024.0);
        let cpu_count = self.system.cpus().len();
        let cpu_brand = self.system.global_cpu_info().brand().to_string();
        
        let gpu_info = self.detect_gpus();
        let npu_detected = self.detect_npu();
        
        let os_info = format!("{} {}", 
            self.system.name().unwrap_or_else(|| "Unknown".to_string()),
            self.system.os_version().unwrap_or_else(|| "Unknown".to_string())
        );
        
        HardwareInfo {
            total_memory_gb,
            cpu_count,
            cpu_brand,
            gpu_info,
            npu_detected,
            os_info,
        }
    }
    
    fn detect_gpus(&self) -> Vec<GpuInfo> {
        let mut gpus = Vec::new();
        
        // Try to detect NVIDIA GPUs via nvidia-ml-py equivalent
        if let Ok(output) = std::process::Command::new("nvidia-smi")
            .arg("--query-gpu=name,memory.total")
            .arg("--format=csv,noheader,nounits")
            .output()
        {
            if output.status.success() {
                let output_str = String::from_utf8_lossy(&output.stdout);
                for line in output_str.lines() {
                    if let Some((name, vram)) = line.split_once(", ") {
                        if let Ok(vram_mb) = vram.trim().parse::<f64>() {
                            gpus.push(GpuInfo {
                                name: name.trim().to_string(),
                                vram_gb: Some(vram_mb / 1024.0),
                                vendor: "NVIDIA".to_string(),
                            });
                        }
                    }
                }
            }
        }
        
        // Try to detect AMD GPUs
        if let Ok(output) = std::process::Command::new("rocm-smi")
            .arg("--showmeminfo")
            .arg("vram")
            .output()
        {
            if output.status.success() {
                // Parse AMD GPU info - this is a simplified version
                // In practice, you'd need more sophisticated parsing
                gpus.push(GpuInfo {
                    name: "AMD GPU".to_string(),
                    vram_gb: Some(8.0), // Placeholder - would need actual detection
                    vendor: "AMD".to_string(),
                });
            }
        }
        
        // Fallback detection for integrated/basic GPUs
        if gpus.is_empty() {
            // Check for common GPU indicators in system info
            let cpu_brand_lower = self.system.global_cpu_info().brand().to_lowercase();
            
            if cpu_brand_lower.contains("intel") {
                gpus.push(GpuInfo {
                    name: "Intel Integrated Graphics".to_string(),
                    vram_gb: None,
                    vendor: "Intel".to_string(),
                });
            } else if cpu_brand_lower.contains("amd") {
                gpus.push(GpuInfo {
                    name: "AMD Integrated Graphics".to_string(),
                    vram_gb: None,
                    vendor: "AMD".to_string(),
                });
            }
        }
        
        gpus
    }
    
    fn detect_npu(&self) -> bool {
        // Check for Apple Neural Engine (M1/M2/M3 chips)
        if cfg!(target_os = "macos") {
            let cpu_brand = self.system.global_cpu_info().brand().to_lowercase();
            if cpu_brand.contains("apple") {
                return true;
            }
        }
        
        // Check for Intel Neural Processing Unit
        if let Ok(output) = std::process::Command::new("lspci").output() {
            let output_str = String::from_utf8_lossy(&output.stdout).to_lowercase();
            if output_str.contains("neural") || output_str.contains("npu") {
                return true;
            }
        }
        
        // Check for Qualcomm NPU (Windows)
        if cfg!(target_os = "windows") {
            // This would require Windows-specific detection
            // For now, return false as a placeholder
        }
        
        false
    }
}