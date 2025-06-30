Write-Host '🚀 Executando testes do projeto Aurora...' -ForegroundColor Cyan

# Detecta o ambiente virtual do Poetry
$venvPath = poetry env info --path
$venvScripts = Join-Path $venvPath 'Scripts'

# Corrige o PATH e PYTHONPATH temporariamente
$env:PATH = "$venvScripts;$env:PATH"
try {
    $env:PYTHONPATH = (Resolve-Path ./src).Path
    Write-Host "PYTHONPATH setado para ./src" -ForegroundColor Yellow
} catch {
    Write-Host "AVISO: Diretório ./src não encontrado." -ForegroundColor Red
}

# Verifica se pytest existe, senão instala
$pytestExe = Join-Path $venvScripts 'pytest.exe'
if (-Not (Test-Path $pytestExe)) {
    Write-Host "pytest não encontrado no ambiente virtual. Instalando..." -ForegroundColor Yellow
    & "$venvScripts\pip.exe" install pytest
}

# Executa os testes
Write-Host "Iniciando testes com pytest..."
& $pytestExe

Write-Host '✅ Testes finalizados. Tudo limpo, como o cache de um deploy bem feito.' -ForegroundColor Green