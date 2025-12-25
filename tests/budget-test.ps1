$ErrorActionPreference = 'Stop'
$Base = 'http://localhost:8000'
# Set budget to tiny limits and enforce
$cfgBody = @{ daily_limit_usd = 0.00001; monthly_limit_usd = 0.00001; enforce = $true; cost_per_token_usd = 0.0001 } | ConvertTo-Json
Invoke-RestMethod -Uri "$Base/api/v1/budget/config" -Method Post -ContentType 'application/json' -Body $cfgBody | Out-Null

# First chat
$chat1 = @{ message = 'Use some tokens.'; mode = 'chat'; stream = $false } | ConvertTo-Json
$r1 = Invoke-RestMethod -Uri "$Base/api/v1/chat/send" -Method Post -ContentType 'application/json' -Body $chat1
"First response event content: " + ($r1 | Where-Object { $_.type -eq 'response' } | Select-Object -First 1 -ExpandProperty content)

# Second chat (should be blocked)
$chat2 = @{ message = 'Use more tokens again.'; mode = 'chat'; stream = $false } | ConvertTo-Json
$r2 = Invoke-RestMethod -Uri "$Base/api/v1/chat/send" -Method Post -ContentType 'application/json' -Body $chat2
"Second response event content: " + ($r2 | Where-Object { $_.type -eq 'response' } | Select-Object -First 1 -ExpandProperty content)
