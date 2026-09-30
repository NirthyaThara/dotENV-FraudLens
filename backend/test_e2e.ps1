# e2e_test.ps1

$base = "http://localhost:8000"
$headers = @{ "X-API-Key" = "test_secret_key_123" }

Write-Host "1. Testing Health Check (No Auth)" -ForegroundColor Cyan
$r1 = Invoke-WebRequest -Uri "$base/" -Method GET -UseBasicParsing
Write-Host "Status: $($r1.StatusCode) - $($r1.Content)`n"

Write-Host "2. Testing Auth Failure (No API Key on write endpoint)" -ForegroundColor Cyan
try {
    $r2 = Invoke-WebRequest -Uri "$base/transactions" -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)`n"
}

Write-Host "3. Testing Successful Transaction & Fraud Engine (Impossible Travel)" -ForegroundColor Cyan
# Reset demo data
Invoke-WebRequest -Uri "$base/demo/reset" -Method DELETE -Headers $headers -UseBasicParsing | Out-Null
# Run simulation
$r3 = Invoke-WebRequest -Uri "$base/simulate/impossible_travel" -Method POST -Headers $headers -UseBasicParsing
Write-Host "Simulation run:" -ForegroundColor Green
$r3.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3

Write-Host "`n4. Testing Audit Log (Reviewing the flag)" -ForegroundColor Cyan
# Get the flag id
$flags = Invoke-WebRequest -Uri "$base/flags" -Method GET -Headers $headers -UseBasicParsing | ConvertFrom-Json
if ($flags.items.Count -gt 0) {
    $flagId = $flags.items[0].id
    $body = '{"comment": "User confirmed travel to London"}'
    $r4 = Invoke-WebRequest -Uri "$base/flags/$flagId/review" -Method PATCH -Headers $headers -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "Flag reviewed:" -ForegroundColor Green
    $r4.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
}

Write-Host "`nAll tests completed!" -ForegroundColor Cyan
