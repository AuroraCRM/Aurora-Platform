import re
from unidecode import unidecode

class CNPJAdapter:
    @staticmethod
    def normalize_text(text: str) -> str:
        """Remove caracteres especiais e normaliza encodings"""
        if not text:
            return ""
        # Remove caracteres não-ASCII e normaliza espaços
        normalized = unidecode(text).strip()
        # Remove múltiplos espaços
        return re.sub(r'\s+', ' ', normalized)
    
    @staticmethod
    def adapt_receitaws_response(api_data: dict) -> dict:
        """Adapta a resposta da ReceitaWS para nosso schema"""
        if not api_data or 'status' in api_data and api_data['status'] == 'ERROR':
            return None
        
        return {
            "cnpj": api_data.get("cnpj", ""),
            "razao_social": CNPJAdapter.normalize_text(api_data.get("nome", "")),
            "nome_fantasia": CNPJAdapter.normalize_text(api_data.get("fantasia", "")),
            "atividade_principal": CNPJAdapter.normalize_text(
                api_data.get("atividade_principal", [{}])[0].get("text", "")
            ),
            "situacao_cadastral": CNPJAdapter.normalize_text(api_data.get("situacao", "")),
            "endereco": {
                "logradouro": CNPJAdapter.normalize_text(api_data.get("logradouro", "")),
                "numero": api_data.get("numero", ""),
                "complemento": CNPJAdapter.normalize_text(api_data.get("complemento", "")),
                "cep": api_data.get("cep", "").replace('.', ''),
                "municipio": CNPJAdapter.normalize_text(api_data.get("municipio", "")),
                "uf": api_data.get("uf", "")
            }
        }