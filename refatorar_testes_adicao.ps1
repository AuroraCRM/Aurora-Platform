$folderPath = "C:\Users\winha\Aurora\CRM Q"  # Pasta raiz
$selectedFiles = @("tests/test_api.py", "tests/test_integracao_cnpj.py", "tests/test_api_leads.py")  # Arquivos-alvo

# Percorre os arquivos e ajusta as funções de teste
foreach ($fileName in $selectedFiles) {
    $filePath = Join-Path $folderPath $fileName
    if (Test-Path $filePath) {
        (Get-Content $filePath) | ForEach-Object {
            $_ -replace '^(def test_[^(]+)\(', '$1(client, '  # Adiciona 'client' como argumento
        } | Set-Content $filePath

        Write-Output "Arquivo atualizado: $filePath"
    } else {
        Write-Output "Arquivo não encontrado: $filePath"
    }
}