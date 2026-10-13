$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot '..\data') -Force | Out-Null
foreach ($symbol in @('2330', '2382', '6669', '3017')) {
    $uri = "https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id=$symbol&start_date=2025-01-01"
    $headers = @{}
    if ($env:FINMIND_TOKEN) { $headers['Authorization'] = "Bearer $env:FINMIND_TOKEN" }
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -TimeoutSec 30
    if ($response.status -ne 200 -or $response.data.Count -eq 0) { throw "No valid data for $symbol" }
    $response | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot "..\data\$symbol.json") -Encoding utf8
    Write-Output "$symbol : $($response.data.Count) bars"
    Start-Sleep -Seconds 1
}
