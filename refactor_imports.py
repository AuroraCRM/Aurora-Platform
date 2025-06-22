import os
import re
from pathlib import Path

def refactor_imports(file_path: Path):
    """Refatora os imports no arquivo conforme padrão Aurora"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Padrão para identificar imports que começam com 'src'
    pattern = r'(from\s+)(src\.)(\S+?\s+import\s+[\w\s,]+)'
    
    # Substitui 'src.' por 'aurora.'
    new_content = re.sub(pattern, r'\1aurora.\3', content)
    
    # Padrão para imports completos
    pattern_full = r'(import\s+)(src\.)(\S+)'
    new_content = re.sub(pattern_full, r'\1aurora.\3', new_content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Refatorado: {file_path}")

def main():
    project_root = Path.cwd()
    directories = ['src', 'tests']
    
    print("Iniciando refatoração de imports...")
    print("Padrão: 'src' → 'aurora'")
    
    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            continue
            
        print(f"\nProcessando: {dir_path}")
        
        for file_path in dir_path.rglob('*.py'):
            refactor_imports(file_path)
    
    print("\nRefatoração concluída com sucesso!")

if __name__ == '__main__':
    main()  