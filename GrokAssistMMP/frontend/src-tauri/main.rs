#![cfg_attr(all(not(debug_assertions), target_os = "windows"), windows_subsystem = "windows")]

use tauri::{Manager, Window};
use anyhow::{Result, anyhow};
use ort::{Environment, ExecutionProvider, SessionBuilder, GraphOptimizationLevel};
use nvml_wrapper::{Nvml, enum_wrappers::device::MemoryInfo};
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use pv_porcupine::{PorcupineBuilder, Porcupine};
use whisper_rs::{FullParams, SamplingStrategy, WhisperContext, WhisperState};
use tts::TTS;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use std::collections::VecDeque;
use reqwest;

#[derive(Clone, serde::Serialize)]
struct Payload {
    message: String,
}

struct AppState {
    tier: Mutex<String>,
}

#[tauri::command]
fn detect_tier() -> Result<String, String> {
    let env = Environment::builder()
        .with_name("detect")
        .build()
        .map_err(|e| e.to_string())?;

    let mut tier = "light".to_string();

    if ExecutionProvider::CUDA(Default::default()).is_available() {
        match Nvml::init() {
            Ok(nvml) => {
                if let Ok(device_count) = nvml.device_count() {
                    if device_count > 0 {
                        if let Ok(device) = nvml.device_by_index(0) {
                            if let Ok(mem_info) = device.memory_info() {
                                let vram_gb = mem_info.total / (1024 * 1024 * 1024);
                                if vram_gb > 8 {
                                    tier = "heavy".to_string();
                                } else if vram_gb >= 4 {
                                    tier = "medium".to_string();
                                }
                            }
                        }
                    }
                }
            }
            Err(_) => {}
        }
    } else if ExecutionProvider::CoreML(Default::default()).is_available() ||
              ExecutionProvider::OpenVINO(Default::default()).is_available() {
        tier = "npu".to_string();
    }

    Ok(tier)
}

#[tauri::command]
fn set_tier_to_backend(tier: String) -> Result<(), String> {
    let client = reqwest::blocking::Client::new();
    client.post("http://localhost:8000/set_tier")
        .json(&serde_json::json!({"tier": tier}))
        .send()
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn start_voice_loop(window: Window) -> Result<(), String> {
    std::thread::spawn(move || -> Result<()> {
        let porcupine = PorcupineBuilder::new_with_keywords(&["bumblebee"])
            .init()?;

        let host = cpal::default_host();
        let device = host.default_input_device().ok_or(anyhow!("No input device"))?;
        let config = device.default_input_config()?.into();

        let audio_buffer: Arc<Mutex<VecDeque<i16>>> = Arc::new(Mutex::new(VecDeque::new()));
        let audio_buffer_clone = audio_buffer.clone();

        let stream = device.build_input_stream(
            &config,
            move |data: &[i16], _: &cpal::InputCallbackInfo| {
                let mut buffer = audio_buffer_clone.lock().unwrap();
                buffer.extend(data.iter().cloned());
            },
            |err| eprintln!("Audio error: {}", err),
            None,
        )?;
        stream.play()?;

        loop {
            {
                let mut buffer = audio_buffer.lock().unwrap();
                if buffer.len() >= porcupine.frame_length() as usize {
                    let frame: Vec<i16> = buffer.drain(0..porcupine.frame_length() as usize).collect();
                    if let Ok(keyword_index) = porcupine.process(&frame) {
                        if keyword_index >= 0 {
                            // Wake word detected, record for STT (simplified: collect 5s audio)
                            std::thread::sleep(Duration::from_secs(5));
                            let mut recording: Vec<f32> = Vec::new();
                            {
                                let mut buf = audio_buffer.lock().unwrap();
                                recording = buf.iter().map(|&s| s as f32 / 32768.0).collect();
                                buf.clear();
                            }
                            // STT with whisper-rs (assume model downloaded to ./ggml-base.en.bin)
                            let ctx = WhisperContext::new("./ggml-base.en.bin")?;
                            let mut state = ctx.create_state()?;
                            let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });
                            params.set_sample_rate(16000);
                            state.full(params, &recording)?;
                            let mut text = String::new();
                            for i in 0..state.full_n_segments()? {
                                text.push_str(&state.full_get_segment_text(i)?);
                            }
                            // Send to backend
                            let client = reqwest::blocking::Client::new();
                            let resp = client.post("http://localhost:8000/chat")
                                .json(&serde_json::json!({"query": text.trim(), "conv_id": 0}))
                                .send()?
                                .json::<serde_json::Value>()?;
                            let ai_response = resp["response"].as_str().ok_or(anyhow!("No response"))?.to_string();
                            // Emit to UI
                            window.emit("voice-response", Payload { message: ai_response.clone() })?;
                            // TTS
                            let mut tts = TTS::default()?;
                            tts.speak(ai_response, false)?;
                        }
                    }
                }
            }
            std::thread::sleep(Duration::from_millis(10));
        }
    });
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .manage(AppState { tier: Mutex::new("light".to_string()) })
        .invoke_handler(tauri::generate_handler![detect_tier, set_tier_to_backend, start_voice_loop])
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}