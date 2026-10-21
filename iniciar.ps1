# Inicia a interface local. Execute na pasta do projeto com PowerShell.
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\adk.exe web --host 127.0.0.1 --port 8000
