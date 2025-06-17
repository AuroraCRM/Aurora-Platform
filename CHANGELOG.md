# Changelog

## [Não Versionado] - 2024-11-XX

### Correções
- Resolvidos conflitos de merge em vários arquivos
- Corrigido o arquivo `servico_crm.py` para unificar as funcionalidades
- Corrigido o arquivo `database_config.py` para usar as configurações centralizadas
- Corrigido o arquivo `cliente_schemas.py` para usar a sintaxe correta do Pydantic v2
- Adicionada importação de httpx no arquivo `servico_crm.py`

### Adicionado
- Implementado o repositório `cliente_repository.py` que estava faltando
- Criado o roteador `cliente_router.py` para endpoints de clientes
- Criado o roteador `lead_router.py` para endpoints de leads
- Criado o modelo `lead_models.py` para leads
- Criado o esquema `lead_schemas.py` para validação de leads
- Adicionado script `init_db.py` para inicialização do banco de dados
- Adicionado script `check_setup.py` para verificar a configuração do ambiente
- Adicionado script `run_tests.py` para executar os testes
- Atualizado o arquivo `run_api.py` para inicializar o banco de dados antes de iniciar o servidor
- Atualizado o arquivo `main.py` na raiz para evitar conflitos
- Atualizado o arquivo `README.md` com informações detalhadas sobre o projeto
- Criado arquivo `.env.example` com modelo para configuração

### Modificado
- Atualizado o arquivo `requirements.txt` para incluir todas as dependências necessárias
- Atualizado o arquivo `main.py` para incluir todos os roteadores
- Unificadas as funções de serviço em `servico_crm.py`