$dest = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Recurse -Force (Join-Path $PSScriptRoot "skills\*") $dest
Write-Host "Installed skills into $dest. Restart Claude Code to load them."
