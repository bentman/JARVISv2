# Desktop Packaging (Tauri)

## Prerequisites

- Windows:
  - Rust toolchain (stable)
  - Visual Studio Build Tools (C++)
  - WebView2 runtime
- macOS:
  - Xcode Command Line Tools
  - Codesigning identity for distribution (optional)
- Linux:
  - libgtk-3-dev, libayatana-appindicator3-dev, webkit2gtk-4.0, patchelf, librsvg2-dev
  - See https://tauri.app for distro-specific guidance

## Development

- `cd frontend && npm install && npm run dev`
- `cargo tauri dev`

## Production

- Frontend build: `cd frontend && npm run build`
- Package installers: from `frontend`, `cargo tauri build`
- Output installers are platform-specific under `frontend/src-tauri/target/release/bundle`