# Define a pasta raiz do projeto
$folderPath = "C:\Users\winha\Aurora\CRM Q"

# Lista dos arquivos específicos que precisam ser atualizados
$selectedFiles = @(
    "tests/test_api.py",
    "tests/test_api_leads.py",
    "tests/test_integracao_cnpj.py",
    "tests/test_api_mock.py"
)

# Textos exatos a serem removidos
$searchText = @(
    "from fastapi.testclient import TestClient",
    "client = TestClient(app)"
)

# O texto de substituição será uma string vazia, efetivamente deletando a linha

# --- Início da Lógica de Substituição ---

Write-Output "Iniciando refatoração dos arquivos de teste..."

foreach ($fileName in $selectedFiles) {
    $filePath = Join-Path $folderPath $fileName
    
    if (Test-Path $filePath) {
        # Lê o conteúdo, substitui as linhas e salva o arquivo de volta
        $originalContent = Get-Content $filePath -Raw
        $modifiedContent = $originalContent

        foreach ($text in $searchText) {
            # Usa -split e -join para remover a linha inteira, incluindo a quebra de linha
            $modifiedContent = ($modifiedContent -split "`r?`n") | Where-Object { $_ -notmatch [regex]::Escape($text) } | Out-String
        }

        Set-Content -Path $filePath -Value $modifiedContent.Trim()
        
        Write-Output "[OK] Arquivo atualizado: $filePath"
    } else {
        Write-Output "[AVISO] Arquivo não encontrado, pulando: $filePath"
    }
}

Write-Output "Refatoração concluída."