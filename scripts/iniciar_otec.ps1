$ErrorActionPreference = 'Stop'
$otecRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $otecRoot
if (Test-Path -LiteralPath '.local/mysql-process.json') { & "$PSScriptRoot/iniciar_mysql.ps1" }
& "$otecRoot/.venv/Scripts/python.exe" manage.py runserver 127.0.0.1:8000
