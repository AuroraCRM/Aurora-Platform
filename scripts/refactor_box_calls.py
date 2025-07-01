# scripts/refactor_box_calls.py

import re
from pathlib import Path
import sys

def refatorar_chamadas_box(diretorio_raiz: str):
    """
    Varre um diretório em busca de chamadas de método incorretas em objetos
    de configuração (ex: settings.FOO()) e as corrige para acesso a atributos
    (ex: settings.FOO) de forma interativa.
    """
    padrao = re.compile(r"(\b(?:settings|config)\b\.\w+)\(\)")
    caminho_raiz = Path(diretorio_raiz)
    arquivos_py = list(caminho_raiz.rglob("*.py"))

    print(f"--- Iniciando refatoração interativa em {len(arquivos_py)} arquivos ---")

    arquivos_modificados = 0
    for caminho_arquivo in arquivos_py:
        try:
            conteudo_original = caminho_arquivo.read_text(encoding="utf-8")
            novo_conteudo = conteudo_original
            modificacoes_no_arquivo = []

            for match in padrao.finditer(conteudo_original):
                linha_num = conteudo_original.count('\n', 0, match.start()) + 1
                linha_original = conteudo_original.splitlines()[linha_num - 1]
                
                print("\n" + "="*50)
                print(f"ERRO ENCONTRADO EM: {caminho_arquivo}:{linha_num}")
                print(f"  LINHA ORIGINAL: {linha_original.strip()}")
                
                correcao_proposta = padrao.sub(r"\1", match.group(0))
                print(f"  CORREÇÃO PROPOSTA: {correcao_proposta}")

                while True:
                    resposta = input("  Aprovar esta correção? (s/n): ").lower().strip()
                    if resposta in ['s', 'n']:
                        break
                    print("  Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")

                if resposta == 's':
                    # Armazena a correção para aplicar depois
                    modificacoes_no_arquivo.append((match.group(0), correcao_proposta))
                    print(f"  >>> Correção APROVADA.")
                else:
                    print(f"  >>> Correção IGNORADA.")
            
            # Aplica todas as modificações aprovadas para este arquivo de uma vez
            if modificacoes_no_arquivo:
                temp_conteudo = conteudo_original
                for original, corrigido in modificacoes_no_arquivo:
                    # Usamos replace com count=1 para substituir uma ocorrência de cada vez
                    temp_conteudo = temp_conteudo.replace(original, corrigido, 1)
                
                caminho_arquivo.write_text(temp_conteudo, encoding="utf-8")
                arquivos_modificados += 1
                print(f"\n[SALVO] O arquivo {caminho_arquivo} foi atualizado com as correções aprovadas.")
                print("="*50)


        except Exception as e:
            print(f"ERRO ao processar o arquivo {caminho_arquivo}: {e}", file=sys.stderr)

    print(f"\n--- Refatoração concluída. {arquivos_modificados} arquivo(s) modificado(s). ---")


if __name__ == "__main__":
    # Define o diretório 'src' como o alvo da refatoração
    diretorio_alvo = "src"
    refatorar_chamadas_box(diretorio_alvo)