# Local AI Assistant Installation Guide

## System Requirements

### Minimum Requirements
- **CPU**: Dual-core processor
- **RAM**: 8GB
- **Disk Space**: 10GB available
- **OS**: Windows 10+, macOS 12+, Ubuntu 20.04+

### Recommended Requirements
- **CPU**: 4+ cores
- **GPU**: 4GB+ VRAM (NVIDIA/AMD/Intel)
- **RAM**: 16GB
- **Disk Space**: 20GB available

### Optimal Requirements
- **CPU**: 8+ cores
- **GPU**: 8GB+ VRAM (NVIDIA RTX 3070+/AMD RX 6700+/Intel Arc)
- **RAM**: 32GB
- **Disk Space**: 50GB available

## Installation Steps

### 1. Install Docker Desktop

Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)

### 2. Download the Application

Download the appropriate installer for your operating system:

- **Windows**: `LocalAIAssistant-Setup.exe`
- **macOS**: `LocalAIAssistant.dmg`
- **Linux**: `LocalAIAssistant.AppImage`

### 3. Install the Application

#### Windows
1. Double-click the downloaded `.exe` file
2. Follow the installation wizard
3. The application will be installed to `C:\Program Files\LocalAIAssistant`

#### macOS
1. Double-click the downloaded `.dmg` file
2. Drag the application to your Applications folder
3. The application will be installed to `/Applications/LocalAIAssistant`

#### Linux
1. Make the AppImage executable:
   ```bash
   chmod +x LocalAIAssistant.AppImage
   ```
2. Run the AppImage:
   ```bash
   ./LocalAIAssistant.AppImage
   ```

### 4. Install AI Models

The application requires local AI models to function. Models will be automatically downloaded on first launch, but you can also manually install them:

1. Create a `models` folder in the application directory
2. Download GGUF format models and place them in the models folder

### 5. First Launch

1. Launch the application from your desktop or applications folder
2. The application will automatically detect your hardware capabilities
3. If models are not found, the application will prompt you to download them
4. Configure privacy settings as desired

## Initial Configuration

### Privacy Settings

On first launch, you'll be prompted to configure privacy settings:

1. **Data Retention**: Choose how long to keep conversation history
2. **Cloud Processing**: Enable or disable cloud processing (disabled by default)
3. **Data Classification**: Configure what types of data should never leave your device

### Voice Settings

1. **Wake Word**: Configure the wake word for voice activation
2. **Voice Model**: Select the voice model for text-to-speech
3. **Input Device**: Select the microphone for speech-to-text

## Updating the Application

### Automatic Updates

The application will automatically check for updates on launch. When an update is available, you'll be prompted to install it.

### Manual Updates

1. Download the latest installer from the official website
2. Run the installer
3. The application will be updated automatically

## Uninstalling the Application

### Windows
1. Open "Apps & features" in Settings
2. Find "Local AI Assistant"
3. Click "Uninstall"

### macOS
1. Drag the application from your Applications folder to the Trash
2. Empty the Trash

### Linux
1. Delete the AppImage file
2. Optionally, delete the application data directory

## Troubleshooting

### Common Issues

1. **Application won't start**: Ensure Docker Desktop is running
2. **Models not downloading**: Check your internet connection and firewall settings
3. **Voice not working**: Check microphone permissions in system settings
4. **Slow responses**: Verify your hardware meets the recommended requirements

### Getting Help

If you encounter issues not covered in this guide:

1. Check the application logs in the data directory
2. Visit our support website at [support.local-ai-assistant.com](https://support.local-ai-assistant.com)
3. Contact support at support@local-ai-assistant.com