#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, 
    SystemTrayMenuItem, Window, WindowEvent
};
use tracing_subscriber;

mod api;
mod audio;
mod hardware;
mod speech;

use api::ApiClient;
use hardware::HardwareDetector;
use speech::{SpeechToText, TextToSpeech};

#[derive(Clone, serde::Serialize)]
struct Payload {
    message: String,
}

#[tauri::command]
async fn send_chat_message(
    message: String,
    message_type: Option<String>,
    state: tauri::State<'_, AppState>,
) -> Result<api::ChatResponse, String> {
    state.api_client
        .send_chat_message(&message, message_type.as_deref())
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn get_hardware_info(
    state: tauri::State<'_, AppState>,
) -> Result<serde_json::Value, String> {
    state.api_client
        .get_hardware_info()
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn get_memory(
    limit: Option<u32>,
    offset: Option<u32>,
    state: tauri::State<'_, AppState>,
) -> Result<Vec<api::MemoryEntry>, String> {
    state.api_client
        .get_memory(limit, offset)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn start_voice_recording(
    state: tauri::State<'_, AppState>,
) -> Result<(), String> {
    state.speech_to_text
        .start_recording()
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn stop_voice_recording(
    state: tauri::State<'_, AppState>,
) -> Result<String, String> {
    state.speech_to_text
        .stop_recording_and_transcribe()
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn speak_text(
    text: String,
    state: tauri::State<'_, AppState>,
) -> Result<(), String> {
    state.text_to_speech
        .speak(&text)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
async fn check_backend_health(
    state: tauri::State<'_, AppState>,
) -> Result<bool, String> {
    Ok(state.api_client.health_check().await.is_ok())
}

struct AppState {
    api_client: ApiClient,
    hardware_detector: HardwareDetector,
    speech_to_text: SpeechToText,
    text_to_speech: TextToSpeech,
}

fn create_system_tray() -> SystemTray {
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

fn main() {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    let system_tray = create_system_tray();

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    std::process::exit(0);
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "hide" => {
                    let window = app.get_window("main").unwrap();
                    window.hide().unwrap();
                }
                _ => {}
            },
            _ => {}
        })
        .on_window_event(|event| match event.event() {
            WindowEvent::CloseRequested { api, .. } => {
                event.window().hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
        .setup(|app| {
            let api_client = ApiClient::new("http://localhost:8080".to_string());
            let hardware_detector = HardwareDetector::new();
            let speech_to_text = SpeechToText::new().expect("Failed to initialize STT");
            let text_to_speech = TextToSpeech::new().expect("Failed to initialize TTS");

            app.manage(AppState {
                api_client,
                hardware_detector,
                speech_to_text,
                text_to_speech,
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            send_chat_message,
            get_hardware_info,
            get_memory,
            start_voice_recording,
            stop_voice_recording,
            speak_text,
            check_backend_health
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}