$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pidPath = Join-Path $projectRoot 'reports\monitor.pid'
if (-not (Test-Path -LiteralPath $pidPath)) { Write-Output 'No saved monitor process'; exit }
$monitorPid = [int](Get-Content -LiteralPath $pidPath)
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$monitorPid"
if ($process -and $process.CommandLine.Contains((Join-Path $projectRoot 'monitor.py'))) {
    Stop-Process -Id $monitorPid
    Write-Output 'Monitor stopped'
} else { Write-Output 'Saved monitor process is no longer running' }
