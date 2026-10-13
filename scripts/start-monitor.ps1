param([string]$PythonPath = 'python')
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$reportsPath = Join-Path $projectRoot 'reports'
New-Item -ItemType Directory -Path $reportsPath -Force | Out-Null
$pidPath = Join-Path $reportsPath 'monitor.pid'
if (Test-Path -LiteralPath $pidPath) {
    $oldPid = [int](Get-Content -LiteralPath $pidPath)
    $oldProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$oldPid"
    if ($oldProcess -and $oldProcess.CommandLine.Contains((Join-Path $projectRoot 'monitor.py'))) {
        Write-Output "Monitor already running: $oldPid"
        exit
    }
}
$monitorScript = Join-Path $projectRoot 'monitor.py'
$env:PYTHONIOENCODING = 'utf-8'
$process = Start-Process -FilePath $PythonPath -ArgumentList @('-u', "`"$monitorScript`"") -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $reportsPath 'monitor.log') -RedirectStandardError (Join-Path $reportsPath 'monitor-error.log')
$process.Id | Set-Content -LiteralPath $pidPath
Write-Output "Monitor started: $($process.Id). Open http://127.0.0.1:8765/entry-dashboard.html"
