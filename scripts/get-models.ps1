<#
.SYNOPSIS
Downloads required models for the Local AI Assistant based on the specified environment (dev or prod).

.DESCRIPTION
This script downloads AI models (LLM, TTS, STT) appropriate for either development or production use. 
For development, it downloads smaller models for faster iteration. For production, it downloads optimized models for better performance.

.PARAMETER Environment
Specifies the environment: 'dev' for development models or 'prod' for production models. Default is 'prod'.

.PARAMETER ModelsDir
Directory to download models to. Default is 'models'.

.EXAMPLE
./get-models.ps1 -Environment dev
Downloads development models to the default 'models' directory.

.EXAMPLE
./get-models.ps1 -Environment prod -ModelsDir "C:\prod-models"
Downloads production models to the specified directory.
#>

param(
    [ValidateSet('dev', 'prod')]
    [string]$Environment = 'prod',
    
    [string]$ModelsDir = 'models'
)

# Create models directory if it doesn't exist
if (-Not (Test-Path $ModelsDir)) { 
    New-Item -ItemType Directory -Path $ModelsDir | Out-Null 
    Write-Host "Created directory: $ModelsDir" -ForegroundColor Green
}

Set-Location $ModelsDir

# Determine model URLs based on environment
if ($Environment -eq 'dev') {
    Write-Host "Downloading development models (smaller, faster)..." -ForegroundColor Yellow
    
    # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
    $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
    $TllFile = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
}
else {
    Write-Host "Downloading production models (optimized for performance)..." -ForegroundColor Green
    
    # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
    $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
    $TllFile = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
}

# Download LLM model if not present
if (-Not (Test-Path $TllFile)) {
    Write-Host "Downloading $TllFile ..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $TllUrl -OutFile $TllFile -ErrorAction Stop
    if (-Not (Test-Path $TllFile)) { throw "Download failed for $TllFile" }
    Write-Host "Successfully downloaded $TllFile" -ForegroundColor Green
} else {
    Write-Host "$TllFile already exists, skipping download." -ForegroundColor Gray
}

# Piper English voice (common for both environments)
$PiperUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx"
$PiperFile = "en_US-amy-low.onnx"
$PiperJsonUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json"
$PiperJsonFile = "en_US-amy-low.onnx.json"

if (-Not (Test-Path $PiperFile)) {
    Write-Host "Downloading $PiperFile (TTS)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $PiperUrl -OutFile $PiperFile -ErrorAction Stop
    if (-Not (Test-Path $PiperFile)) { throw "Download failed for $PiperFile" }
    Write-Host "Successfully downloaded $PiperFile" -ForegroundColor Green
} else {
    Write-Host "$PiperFile already exists, skipping download." -ForegroundColor Gray
}

if (-Not (Test-Path $PiperJsonFile)) {
    Write-Host "Downloading $PiperJsonFile (TTS Config)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $PiperJsonUrl -OutFile $PiperJsonFile -ErrorAction Stop
    if (-Not (Test-Path $PiperJsonFile)) { throw "Download failed for $PiperJsonFile" }
    Write-Host "Successfully downloaded $PiperJsonFile" -ForegroundColor Green
} else {
    Write-Host "$PiperJsonFile already exists, skipping download." -ForegroundColor Gray
}

# Whisper Base English (common for both environments)
$WhisperUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
$WhisperFile = "ggml-base.en.bin"
if (-Not (Test-Path $WhisperFile)) {
    Write-Host "Downloading $WhisperFile (STT)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $WhisperUrl -OutFile $WhisperFile -ErrorAction Stop
    if (-Not (Test-Path $WhisperFile)) { throw "Download failed for $WhisperFile" }
    Write-Host "Successfully downloaded $WhisperFile" -ForegroundColor Green
} else {
    Write-Host "$WhisperFile already exists, skipping download." -ForegroundColor Gray
}

# Generate checksums for all model files
Write-Host "Generating checksums..." -ForegroundColor Cyan
$checks = @{}
Get-ChildItem -File | Where-Object { $_.Extension -in ".gguf", ".onnx", ".bin" } | ForEach-Object {
    $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
    $checks[$_.Name] = $sha.Hash
}
($checks | ConvertTo-Json -Depth 3) | Out-File -FilePath "checksums.json" -Encoding utf8
Write-Host "Checksums written to checksums.json" -ForegroundColor Green

Write-Host "Model download complete!" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Green
Write-Host "Models directory: $(Resolve-Path .)" -ForegroundColor Green
