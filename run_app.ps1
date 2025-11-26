# ==========================================
#  Streamlit App Launcher (UTF-8 / Clean)
# ==========================================

Write-Host " Setting up environment..." -ForegroundColor Cyan

# 1. Stop old Streamlit or Python processes
Write-Host " Killing previous Streamlit sessions..."
Get-Process | Where-Object {$_.ProcessName -like "python*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Ensure UTF-8 encoding for all logs
Write-Host "  Setting UTF-8 encoding..."
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

# 3. Create a clean logs folder
Write-Host " Preparing logs folder..."
if (Test-Path "logs") { Remove-Item "logs" -Recurse -Force }
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# 4. Start Streamlit app with safe watcher settings
Write-Host " Launching Streamlit app..."
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = "logs/app_run_$timestamp.log"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "streamlit run app.py --server.fileWatcherType=none --logger.level=debug *>&1 | Out-File -FilePath '$logfile' -Encoding utf8"
)

# 5. Tail the log live in this same window
Write-Host " Live log monitoring started..."
Start-Sleep -Seconds 5
Get-Content $logfile -Wait