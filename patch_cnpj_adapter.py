# patch_cnpj_adapter.py
import os

TARGET_FILE_PATH = "src/integrations/cnpj_adapter.py"

# Este é o conteúdo exato e correto que o arquivo deve ter.
CORRECT_CONTENT = """\
# src/integrations/cnpj_adapter.py
from typing import Any, Dict, Optional
import httpx
from aurora.config import settings

# Obtém a URL base da API do provedor de CNPJ a partir das configurações
CNPJA_BASE_URL = settings.get("CNPJA_API_URL", "https://api.cnpja.com.br/v1")
# Obtém o token de autenticação de forma segura
API_TOKEN = settings.get("CNPJA_API_TOKEN")


class CNPJaAdapter:
    \"\"\"
    Adaptador para se comunicar com a API externa do CNPJá.
    Encapsula a lógica de requisições HTTP e tratamento de respostas.
    \"\"\"

    async def get_cnpj_details(self, cnpj: str) -> Dict[str, Any]:
        \"\"\"
        Busca os detalhes de um CNPJ na API do CNPJá.

        Args:
            cnpj (str): O número do CNPJ a ser consultado.

        Returns:
            Dict[str, Any]: Um dicionário com os dados da empresa.
                            Retorna um dicionário vazio se não encontrar ou ocorrer um erro.
        \"\"\"
        if not API_TOKEN:
            # Lança um erro claro se a configuração essencial estiver faltando
            raise ValueError("API_TOKEN para CNPJá não foi configurado.")

        url = f"{CNPJA_BASE_URL}/companies/{cnpj}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()  # Lança exceção para respostas 4xx ou 5xx
                data = response.json()
                
                # CORREÇÃO CRÍTICA A SER APLICADA
                return data if isinstance(data, dict) else {}

        except httpx.HTTPStatusError as e:
            print(f"Erro ao buscar CNPJ {cnpj}: {e.response.status_code}")
            return {} # Retorna um dicionário vazio em caso de erro de status
        except httpx.RequestError as e:
            print(f"Erro de requisição ao buscar CNPJ {cnpj}: {e}")
            return {} # Retorna um dicionário vazio em caso de erro de rede
"""

def apply_patch():
    """Verifica e aplica o patch no arquivo alvo."""
    print("="*60)
    print(f"PATCH AUTOMATIZADO PARA: {TARGET_FILE_PATH}")
    print("="*60)

    if not os.path.exists(TARGET_FILE_PATH):
        print(f"❌ ERRO: O arquivo alvo não foi encontrado em '{TARGET_FILE_PATH}'.")
        return

    try:
        with open(TARGET_FILE_PATH, 'r', encoding='utf-8') as f:
            current_content = f.read()

        if current_content == CORRECT_CONTENT:
            print("✅ O arquivo já está atualizado. Nenhuma ação necessária.")
        else:
            print("🟡 ALERTA: O conteúdo do arquivo está desatualizado.")
            print("    -> Aplicando patch agora...")
            with open(TARGET_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(CORRECT_CONTENT)
            print("✅ Patch aplicado com sucesso!")
            
    except Exception as e:
        print(f"❌ ERRO INESPERADO: Falha ao ler ou escrever no arquivo. {e}")

if __name__ == "__main__":
    apply_patch()