Write-Host 'Iniciando Poetry Debug Assistant...' -ForegroundColor Cyan

# 1. Forçar ambientes virtuais a serem criados na raiz do projeto
poetry config virtualenvs.in-project true

# 2. Remover ambientes anteriores
Write-Host 'Removendo ambientes Poetry existentes...'
poetry env remove --all

# 3. Definir o Python principal
$pythonPath = (Get-Command python).Source
Write-Host "Usando Python localizado em: $pythonPath"
poetry env use $pythonPath

# 4. Instalar dependências do projeto
Write-Host 'Instalando dependências com poetry install...'
poetry install

# 5. Localizar o caminho do ambiente virtual real
$venvRoot = poetry env info --path
$venvScripts = Join-Path $venvRoot 'Scripts'
$pipPath = Join-Path $venvScripts 'pip.exe'

# 6. Validar se sqlmodel está presente
if (Test-Path $pipPath) {
    & $pipPath show sqlmodel | Select-String Version
    $env:PATH = "$venvScripts;$env:PATH"
    Write-Host 'PATH corrigido para sessão atual.' -ForegroundColor Yellow
} else {
    Write-Host 'AVISO: pip.exe não encontrado no ambiente virtual. Ignorando verificação de sqlmodel.' -ForegroundColor Red
}

# 7. Garantir que PYTHONPATH inclui o diretório src
try {
    $srcPath = Resolve-Path ./src
    $env:PYTHONPATH = "$srcPath"
    Write-Host "PYTHONPATH configurado para: $srcPath"
} catch {
    Write-Host "AVISO: diretório ./src não encontrado. PYTHONPATH não configurado." -ForegroundColor Red
}

# 8. Criar pytest.ini se não existir
if (-not (Test-Path ".\pytest.ini")) {
    "[pytest]`npythonpath = src" | Out-File pytest.ini -Encoding UTF8
    Write-Host 'pytest.ini criado com pythonpath=src'
}

# 9. Executar os testes
Write-Host 'Executando pytest...'
pytest

Write-Host 'Finalizado! Se tudo deu certo, o problema foi enterrado para sempre.' -ForegroundColor Green