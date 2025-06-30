# Encontrar adaptador de rede ativo (com conexão e interface de hardware)
$adaptador = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.HardwareInterface -eq $true } | Select-Object -First 1

if ($adaptador) {
    $nome = $adaptador.Name
    Write-Host "Aplicando DNS para o adaptador ativo: $nome" -ForegroundColor Cyan

    # Definir DNS do Google para IPv4 e IPv6
    Set-DnsClientServerAddress -InterfaceAlias $nome -ServerAddresses @("8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844")

    Write-Host "DNS do Google configurado com sucesso para IPv4 e IPv6!" -ForegroundColor Green
} else {
    Write-Host "Nenhum adaptador de rede ativo encontrado." -ForegroundColor Red
}