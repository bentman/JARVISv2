param(
  [string]$ModelsDir = "models"
)

if (-Not (Test-Path $ModelsDir)) { Write-Host "Models directory not found: $ModelsDir"; exit 1 }
$checksPath = Join-Path $ModelsDir 'checksums.json'
if (-Not (Test-Path $checksPath)) { Write-Host "checksums.json not found in $ModelsDir"; exit 1 }

$checks = Get-Content $checksPath | ConvertFrom-Json
$fail = @()
Get-ChildItem -Path $ModelsDir -File | Where-Object { $_.Extension -in '.gguf','.onnx' } | ForEach-Object {
  $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
  $expected = $checks.$($_.Name)
  if (-not $expected) {
    Write-Host "WARN: No expected hash for $($_.Name)" -ForegroundColor Yellow
  } elseif ($expected -ne $sha.Hash) {
    $fail += $_.Name
    Write-Host "MISMATCH: $($_.Name)" -ForegroundColor Red
  } else {
    Write-Host "OK: $($_.Name)" -ForegroundColor Green
  }
}
if ($fail.Count -gt 0) { Write-Host "Verification failed." -ForegroundColor Red; exit 2 } else { Write-Host "All model files verified." -ForegroundColor Green }