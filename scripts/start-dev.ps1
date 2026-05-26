# Start JobBridge backend + frontend (run from project root)
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting backend on http://localhost:5000 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; `$env:FLASK_ENV='development'; python wsgi.py"

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Write-Host "Done. Open http://localhost:5173"
