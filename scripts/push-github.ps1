# Push to GitHub — sign in as jobbridgepeso-beep first
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "Pushing to https://github.com/jobbridgepeso-beep/PESOPILALAGUNA ..."
git push -u origin main

if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "Push failed. Sign in with the correct GitHub account:"
  Write-Host "  1. Open https://github.com/login"
  Write-Host "  2. Log in as jobbridgepeso-beep"
  Write-Host "  3. Create a Personal Access Token (repo scope)"
  Write-Host "  4. Run: git push -u origin main"
  Write-Host "     Username: jobbridgepeso-beep"
  Write-Host "     Password: <your token>"
}
