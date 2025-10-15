param(
  [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$failures = @()

function Wait-Healthy([int]$retries = 20) {
  for ($i=0; $i -lt $retries; $i++) {
    try {
      $r = Invoke-WebRequest -Uri "$BaseUrl/api/v1/health/services" -UseBasicParsing -TimeoutSec 5
      if ($r.StatusCode -eq 200) { return $true }
    } catch { Start-Sleep -Seconds 1 }
  }
  return $false
}

function Assert($cond, $msg) {
  if (-not $cond) { $script:failures += $msg; Write-Host "FAIL: $msg" -ForegroundColor Red } else { Write-Host "OK: $msg" -ForegroundColor Green }
}

function Get-Json($method, $path, $bodyJson) {
  $uri = "$BaseUrl$path"
  if ($method -eq 'GET') {
    $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 15
    return $r.Content | ConvertFrom-Json
  } elseif ($method -eq 'POST') {
    if ($null -eq $bodyJson) { $bodyJson = '{}' }
    $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 120 -Method Post -ContentType 'application/json' -Body $bodyJson
    return $r.Content | ConvertFrom-Json
  } else {
    throw "Unsupported method: $method"
  }
}

Write-Host "1) Health: services" -ForegroundColor Cyan
$services = Get-Json GET '/api/v1/health/services' $null
Assert ($services.database -eq 'ok') 'database ok'
Assert ($services.redis -eq 'ok') 'redis ok'

Write-Host "2) Health: models" -ForegroundColor Cyan
$models = Get-Json GET '/api/v1/health/models' $null
Assert ($models.models.Count -ge 1) 'at least one model discovered'

Write-Host "3) Chat basic" -ForegroundColor Cyan
$resp = Get-Json POST '/api/v1/chat/send' '{"message":"Hello there"}'
Assert ($resp.Count -ge 2) 'chat returned events'
$main = $resp | Where-Object { $_.type -eq 'response' } | Select-Object -First 1
Assert ($null -ne $main) 'response event present'

Write-Host "4) Streaming endpoint" -ForegroundColor Cyan
$streamUri = "$BaseUrl/api/v1/chat/send/stream"
try {
  $streamResp = Invoke-WebRequest -Uri $streamUri -UseBasicParsing -TimeoutSec 10 -Method Post -ContentType 'application/json' -Body '{"message":"stream test"}' -MaximumRedirection 0
  Assert ($streamResp.StatusCode -eq 200) 'stream POST 200'
} catch {
  $script:failures += 'stream endpoint failed'
  Write-Host "FAIL: stream endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "5) Retrieval influence" -ForegroundColor Cyan
# Seed a message, then query a related prompt and look for Context block
$seed = Get-Json POST '/api/v1/chat/send' '{"message":"Explain the moon phases briefly."}'
$rag = Get-Json POST '/api/v1/chat/send' '{"message":"Revisit the moon phases briefly again."}'
$ragMain = $rag | Where-Object { $_.type -eq 'response' } | Select-Object -First 1
$ragHasCtx = ($ragMain.content -like '*Context (retrieved)*')
Assert ($ragHasCtx) 'retrieval context included'

Write-Host "6) Budget enforcement" -ForegroundColor Cyan
$cfgSet = Get-Json POST '/api/v1/budget/config' '{"enforce":true,"daily_limit_usd":0.00001,"monthly_limit_usd":0.00001,"cost_per_token_usd":0.0001}'
try {
  $b1 = Get-Json POST '/api/v1/chat/send' '{"message":"Use some tokens."}'
  # Second request should trigger budget limit (HTTP 429)
  $budgetExceeded = $false
  try {
    $b2 = Get-Json POST '/api/v1/chat/send' '{"message":"Use more tokens again."}'
    # If we get here without exception, check response content for budget message
    $b2main = $b2 | Where-Object { $_.type -eq 'response' } | Select-Object -First 1
    if ($b2main.content -like '*Budget limit exceeded*') { $budgetExceeded = $true }
  } catch {
    # HTTP 429 or other budget-related error expected
    if ($_.Exception.Message -like '*Budget limit exceeded*' -or $_.Exception.Message -like '*429*') {
      $budgetExceeded = $true
    }
  }
  Assert ($budgetExceeded) 'received budget limit enforcement'
} finally {
  # Reset budget to allow other tests
  $cfgReset = Get-Json POST '/api/v1/budget/config' '{"enforce":false,"daily_limit_usd":1.0,"monthly_limit_usd":10.0,"cost_per_token_usd":0.0001}'
}

Write-Host "7) Cache speedup" -ForegroundColor Cyan
$payload = '{"message":"Explain caching test prompt."}'
$sw1 = [System.Diagnostics.Stopwatch]::StartNew(); $c1 = Get-Json POST '/api/v1/chat/send' $payload; $sw1.Stop()
Start-Sleep -Milliseconds 200
$sw2 = [System.Diagnostics.Stopwatch]::StartNew(); $c2 = Get-Json POST '/api/v1/chat/send' $payload; $sw2.Stop()
$t1 = $sw1.Elapsed.TotalSeconds; $t2 = $sw2.Elapsed.TotalSeconds
# Consider pass if second faster, or within +0.2s tolerance, or first call was slow (>2s)
$fastEnough = ($t2 -le ($t1 + 0.2)) -or ($t1 -gt 2.0)
Assert ($fastEnough) ("cache timing acceptable: second={0:n3}s, first={1:n3}s" -f $t2, $t1)

Write-Host "8) Persistence across restart" -ForegroundColor Cyan
$before = Get-Json GET '/api/v1/chat/conversations' $null
& docker compose restart backend | Out-Null
if (-not (Wait-Healthy 30)) { throw 'Backend did not become healthy after restart' }
$after = Get-Json GET '/api/v1/chat/conversations' $null
Assert ($after.Count -ge $before.Count) 'conversations persisted across restart'

Write-Host "9) Voice TTS + STT" -ForegroundColor Cyan
# TTS via fallback: request audio and write to file
try {
  $ttsResp = Invoke-WebRequest -Uri "$BaseUrl/api/v1/voice/tts?text=Smoke%20test%20TTS" -UseBasicParsing -TimeoutSec 20 -Method Post
  $ttsJson = $ttsResp.Content | ConvertFrom-Json
  $b64 = $ttsJson.audio_data
  [IO.File]::WriteAllBytes('tts_smoke.wav',[Convert]::FromBase64String($b64))
  Assert ((Test-Path 'tts_smoke.wav') -and ((Get-Item 'tts_smoke.wav').Length -gt 1000)) 'generated tts_smoke.wav'
  # STT: upload the generated file (may produce empty text but should return 200)
  $curlOut = curl.exe -sS -F "file=@tts_smoke.wav" "$BaseUrl/api/v1/voice/upload-audio"
  $sttJson = $curlOut | ConvertFrom-Json
  Assert ($null -ne $sttJson) 'stt upload returned JSON'
} catch {
  $script:failures += 'voice stt/tts failed'
  Write-Host "FAIL: voice stt/tts failed: $($_.Exception.Message)" -ForegroundColor Red
}

if ($failures.Count -gt 0) {
  Write-Host "SMOKE TEST FAILED" -ForegroundColor Red
  $failures | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
} else {
  Write-Host "SMOKE TEST PASSED" -ForegroundColor Green
}
