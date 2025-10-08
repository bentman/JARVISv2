param(
  [string]$ModelsDir = "models"
)

if (-Not (Test-Path $ModelsDir)) { New-Item -ItemType Directory -Path $ModelsDir | Out-Null }
Set-Location $ModelsDir

# TinyLlama 1.1B Chat GGUF
$TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
$TllFile = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
if (-Not (Test-Path $TllFile)) {
  Write-Host "Downloading $TllFile ..."
  Invoke-WebRequest -Uri $TllUrl -OutFile $TllFile
}

# Piper English voice (low)
$PiperUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
$PiperFile = "en_US-amy-low.onnx"
if (-Not (Test-Path $PiperFile)) {
  Write-Host "Downloading $PiperFile ..."
  Invoke-WebRequest -Uri $PiperUrl -OutFile $PiperFile
}

# Generate checksums
$checks = @{}
Get-ChildItem -File | Where-Object { $_.Extension -in ".gguf", ".onnx" } | ForEach-Object {
  $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
  $checks[$_.Name] = $sha.Hash
}
($checks | ConvertTo-Json -Depth 3) | Out-File -FilePath "checksums.json" -Encoding utf8
Write-Host "Wrote checksums.json"
