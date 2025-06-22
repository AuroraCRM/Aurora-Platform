# 🤖 Relatório de Ressonância Magnética (MRI) do Projeto Aurora

Análise profunda do diretório: `C:\Users\winha\Aurora\Aurora-Platform\src`

---

## 🩺 Flake8 (Qualidade e Estilo)
**Resultado (Código de Saída: 1)**:
```text

--- ERROS ---
C:\Users\winha\AppData\Local\Programs\Python\Python313\python.exe: No module named flake8
```


## 🛡️ Bandit (Segurança)
**Resultado (Código de Saída: 1)**:
```text

--- ERROS ---
C:\Users\winha\AppData\Local\Programs\Python\Python313\python.exe: No module named bandit
```


## 🧬 MyPy (Consistência de Tipos)
**Resultado (Código de Saída: 1)**:
```text
src\aurora\core\context_engine.py:3: error: Library stubs not installed for "yaml"  [import-untyped]
src\aurora\core\context_engine.py:3: note: Hint: "python3 -m pip install types-PyYAML"
src\aurora\core\context_engine.py:3: note: (or run "mypy --install-types" to install all missing stub packages)
src\aurora\core\context_engine.py:3: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
src\aurora\core\context_engine.py:13: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\auth\two_factor.py:12: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\auth\two_factor.py:16: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\models\lead_models.py:30: error: Need type annotation for "status"  [var-annotated]
src\aurora\ai_core\knowledge_storage.py:26: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\middleware\security.py:20: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\middleware\security.py:24: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\middleware\security.py:28: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
src\aurora\auth\security.py:70: error: Incompatible types in assignment (expression has type "Any | None", variable has type "str")  [assignment]
Found 3 errors in 3 files (checked 50 source files)
```
