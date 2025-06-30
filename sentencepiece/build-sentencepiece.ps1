# build-sentencepiece.ps1
# Script para compilar e instalar a biblioteca sentencepiece a partir do código-fonte.

# Caminho absoluto do diretório do script (deve ser '.../sentencepiece')
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define a pasta do python onde o setup.py está localizado
$PythonDir = Join-Path $Root "python"

Write-Host "`n📦 Gerando a wheel do sentencepiece com setup.py..." -ForegroundColor Cyan
Set-Location $PythonDir

# O setup.py agora está corrigido e cuidará da chamada ao cmake.
python setup.py bdist_wheel

Write-Host "`n🚀 Instalando a wheel gerada localmente..." -ForegroundColor Cyan
$Wheel = Get-ChildItem -Path (Join-Path $PythonDir "dist") -Filter "sentencepiece*.whl" | Select-Object -First 1
pip install $Wheel.FullName --force-reinstall

Write-Host "`n✅ Concluído com sucesso! `n" -ForegroundColor Green