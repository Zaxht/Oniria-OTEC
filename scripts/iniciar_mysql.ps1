$ErrorActionPreference = 'Stop'
$otecRoot = Split-Path -Parent $PSScriptRoot
$otecLocal = Join-Path $otecRoot '.local'
$otecProcessFile = Join-Path $otecLocal 'mysql-process.json'
if (-not (Test-Path -LiteralPath $otecProcessFile)) { throw 'Ejecuta primero scripts/bootstrap_mysql.py.' }
$otecConfig = Get-Content -Raw -LiteralPath $otecProcessFile | ConvertFrom-Json
$otecData = Join-Path $otecLocal 'mysql'
$otecExisting = Get-CimInstance Win32_Process -Filter "Name='mysqld.exe'" | Where-Object { $_.ExecutablePath -eq $otecConfig.mysqld -and $_.CommandLine -and $_.CommandLine.Contains($otecData) }
if ($otecExisting) {
    Write-Output 'La instancia local OTEC ya está iniciada.'
    exit 0
}
$otecArguments = @('--no-defaults', ('--datadir="' + $otecData + '"'), '--port=3307', '--bind-address=127.0.0.1', '--mysqlx=0', '--console')
$otecProcess = Start-Process -FilePath $otecConfig.mysqld -ArgumentList $otecArguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $otecLocal 'mysql-stdout.log') -RedirectStandardError (Join-Path $otecLocal 'mysql-stderr.log')
$otecConfig.pid = $otecProcess.Id
$otecConfig | ConvertTo-Json | Set-Content -LiteralPath $otecProcessFile
Write-Output 'MySQL OTEC iniciado en el puerto 3307.'
