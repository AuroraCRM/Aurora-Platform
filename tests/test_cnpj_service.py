import pytest
from unittest.mock import patch
from aurora.services.cnpj_service import CNPJService
from src.schemas.cnpj_schema import CNPJResponse

def test_consultar_cnpj_success():
    mock_response = {
        "cnpj": "12345678000195",
        "nome": "Emp\u00e9rio Teste Ltda",  # Caractere acentuado proposital
        "fantasia": "Teste & Associados",
        "atividade_principal": [{"text": "Atividade TESTE"}],
        "situacao": "ATIVA",
        "logradouro": "Rua Teste, 123",
        "numero": "123",
        "complemento": "Sala 456",
        "cep": "12345-678",
        "municipio": "São Paulo",
        "uf": "SP"
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        result = CNPJService.consultar_cnpj("12345678000195")
        
        assert isinstance(result, CNPJResponse)
        assert result.razao_social == "Emperio Teste Ltda"  # Verifica normalização
        assert result.atividade_principal == "Atividade TESTE"

def test_invalid_encoding_handling():
    # Simula resposta com encoding problemático
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.apparent_encoding = 'ISO-8859-1'
        mock_get.return_value.text = '{"nome": "Emp\xe9rio Teste"}'
        
        result = CNPJService.consultar_cnpj("12345678000195")
        assert result.razao_social == "Emperio Teste"