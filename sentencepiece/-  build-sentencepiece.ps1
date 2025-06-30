# Caminho absoluto do script
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define pastas importantes
$SourceDir = Join-Path $Root ".."
$BuildDir = Join-Path $SourceDir "build"
$PythonDir = Join-Path $SourceDir "python"

if (!(Test-Path $BuildDir)) {
    New-Item -Path $BuildDir -ItemType Directory | Out-Null
}

Write-Host "`n🛠️  Etapa 1: Gerando build com CMake..." -ForegroundColor Cyan
cmake $SourceDir -A x64 -B $BuildDir -DSPM_ENABLE_SHARED=OFF -DCMAKE_INSTALL_PREFIX="$BuildDir\root"

Write-Host "`n⚙️  Etapa 2: Compilando..." -ForegroundColor Cyan
cmake --build $BuildDir --config Release

Write-Host "`n📦 Etapa 3: Gerando wheel com setup.py..." -ForegroundColor Cyan
Set-Location $PythonDir
python setup.py bdist_wheel

Write-Host "`n🚀 Etapa 4: Instalando a wheel gerada..." -ForegroundColor Cyan
$Wheel = Get-ChildItem "$PythonDir\dist\sentencepiece*.whl" | Select-Object -First 1
pip install $Wheel.FullName

Write-Host "`n✅ Concluído com sucesso! `n" -ForegroundColor Green