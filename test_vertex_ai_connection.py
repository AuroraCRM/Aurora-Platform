# test_vertex_ai_connection.py - Versão Final de Teste de Conexão com .env

import os
from dotenv import load_dotenv # <-- Esta deve ser uma das PRIMEIRAS linhas

# Carrega as variáveis de ambiente do arquivo .env
# IMPORTANTE: Chame load_dotenv() antes de qualquer import do google.cloud.
load_dotenv()

from google.cloud import aiplatform # <-- Importe aqui, após load_dotenv()

# Configura o ID do seu projeto Google Cloud
# O PROJECT_ID e REGION podem ser lidos diretamente do .env agora, ou mantidos fixos.
# Vamos mantê-los fixos por enquanto, mas é bom saber a opção.
PROJECT_ID = "aurora-460619" 
REGION = "us-central1" # A região que você deseja usar (ex: us-central1, southamerica-east1)

def test_vertex_ai_connection():
    print(f"Tentando conectar ao Vertex AI no projeto: {PROJECT_ID}, região: {REGION}")
    
    # Verifica o valor da variável de ambiente APÓS load_dotenv()
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'NÃO DEFINIDO')
    print(f"Usando credenciais de: {creds_path}")

    # Verifica se o caminho das credenciais existe
    if creds_path == 'NÃO DEFINIDO' or not os.path.exists(creds_path):
        print("\n❌ ERRO CRÍTICO: O arquivo de credenciais não foi encontrado ou a variável não foi definida.")
        print(f"Caminho esperado: {os.path.abspath(creds_path)}")
        print("Certifique-se de que GOOGLE_APPLICATION_CREDENTIALS no seu .env está correto e o arquivo JSON existe.")
        return


    try:
        # Inicializa o cliente do Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)

        # Tenta listar os modelos (requer permissões de 'Usuário do Vertex AI' ou similar)
        models = aiplatform.Model.list()

        print("\n✅ Conexão com o Vertex AI bem-sucedida!")
        print(f"Total de modelos encontrados (na sua região): {len(models)}")
        for model in models[:3]: # Mostra os 3 primeiros modelos, se houver
            print(f"  - Modelo: {model.display_name} (ID: {model.name.split('/')[-1]})")

    except Exception as e:
        print("\n❌ Erro na conexão com o Vertex AI:")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {e}")
        print("\nVerifique:")
        print("1. Se o arquivo JSON da conta de serviço existe no caminho especificado por GOOGLE_APPLICATION_CREDENTIALS.")
        print("2. Se a conta de serviço tem as permissões corretas (ex: Usuário do Vertex AI, Administrador de Objetos do Storage).")
        print("3. Se o PROJECT_ID e REGION estão corretos no script e no Google Cloud.")
        print("4. Sua conexão com a internet (especialmente para o Google Cloud).")

if __name__ == "__main__":
    test_vertex_ai_connection()