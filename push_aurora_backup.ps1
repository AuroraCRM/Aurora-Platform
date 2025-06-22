# Caminho do projeto local
Set-Location "C:\Users\winha\Aurora\Aurora-Platform"

Write-Host "📂 Diretório definido para: $(Get-Location)"

# Confirma se existe repositório Git
if (-Not (Test-Path ".git")) {
    Write-Host "🌀 Inicializando repositório Git..."
    git init
}

# Substitui o remote origin pelo novo repositório do GitHub
Write-Host "🔁 Atualizando remote origin para Aurora-Platform..."
git remote remove origin 2>$null
git remote add origin https://github.com/AuroraCRM/Aurora-Platform.git

# Confirma o novo remote
Write-Host "🔍 Remotes configurados:"
git remote -v

# Cria branch main (caso não exista)
Write-Host "🛠️ Definindo branch como main..."
git branch -M main

# Adiciona todos os arquivos e faz commit
Write-Host "➕ Adicionando arquivos ao commit..."
git add .

# Cria um commit
Write-Host "✅ Realizando commit do snapshot atual..."
git commit -m "Backup completo do Projeto Aurora para Aurora-Platform" --allow-empty

# Envia para o GitHub com push forçado
Write-Host "🚀 Enviando para o repositório remoto..."
git push -u origin main --force

Write-Host "`n🎉 Backup enviado com sucesso para https://github.com/AuroraCRM/Aurora-Platform.git"
