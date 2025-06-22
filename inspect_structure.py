import os

def generate_project_tree(startpath):
    """
    Gera uma visualização em árvore da estrutura de diretórios e arquivos.
    """
    # Diretórios e arquivos a serem ignorados na análise
    ignore_list = {'.git', '__pycache__', '.venv', '.vscode', 'build', 'dist', '.pytest_cache'}
    
    print(f"Raio-X do Projeto em: {os.path.abspath(startpath)}")
    print("="*40)
    
    for root, dirs, files in os.walk(startpath):
        # Remove os diretórios ignorados da análise para não percorrê-los
        dirs[:] = [d for d in dirs if d not in ignore_list]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Ignora a impressão do diretório raiz se estivermos no topo
        if level > 0:
            print(f'{indent}|-- {os.path.basename(root)}/')
        
        subindent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            if f not in ignore_list:
                print(f'{subindent}|-- {f}')
    
    print("="*40)
    print("Análise estrutural concluída.")

if __name__ == "__main__":
    # Executa o script a partir do diretório raiz do projeto
    project_root = os.path.dirname(os.path.abspath(__file__))
    generate_project_tree(project_root)