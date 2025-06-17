# Aurora-Platform

## Descrição
Aurora-Platform é uma plataforma de CRM e integração de dados empresariais, fornecendo APIs e serviços para aplicações de negócios com foco em segurança e desempenho.

## Estrutura do Projeto
```
Aurora-Platform/
├── src/
│   └── aurora/
│       ├── auth/          # Autenticação e autorização
│       ├── cache/         # Implementações de cache
│       ├── integrations/  # Integrações com serviços externos
│       ├── middleware/    # Middlewares da aplicação
│       ├── models/        # Modelos de dados
│       ├── repositories/  # Camada de acesso a dados
│       ├── routers/       # Endpoints da API
│       ├── schemas/       # Esquemas de validação
│       ├── services/      # Lógica de negócios
│       └── utils/         # Utilitários e helpers
├── tests/
│   └── unit/             # Testes unitários
├── assets/               # Arquivos estáticos
├── certs/                # Certificados SSL/TLS
├── .env                  # Variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo git
├── Dockerfile            # Configuração do Docker
├── docker-compose.yml    # Configuração do Docker Compose
├── SECURITY.md           # Documentação de segurança
└── README.md             # Este arquivo
```

## Requisitos
- Python 3.8+
- FastAPI
- SQLAlchemy
- Redis
- PostgreSQL (recomendado para produção, SQLite apenas para desenvolvimento)
- Docker e Docker Compose (opcional, para implantação containerizada)

## Instalação

### Método 1: Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Aurora-Platform.git
cd Aurora-Platform
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Copie o arquivo de exemplo de variáveis de ambiente e configure-o:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute o script de verificação de configuração:
```bash
python check_setup.py
```

### Método 2: Instalação com Docker

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Aurora-Platform.git
cd Aurora-Platform
```

2. Copie o arquivo de exemplo de variáveis de ambiente e configure-o:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie os containers com Docker Compose:
```bash
docker-compose up -d
```

## Execução

### Execução Local

```bash
python run_api.py
```

Ou diretamente com uvicorn:

```bash
uvicorn aurora.main:app --reload
```

### Execução com Docker

```bash
docker-compose up -d
```

## Segurança

Este projeto implementa diversas medidas de segurança:

- **Autenticação JWT** com tokens seguros e expiração configurável
- **Controle de acesso baseado em funções** (RBAC)
- **Proteção contra ataques comuns** (XSS, CSRF, SQL Injection)
- **Rate limiting** para prevenir ataques de força bruta
- **Cabeçalhos de segurança HTTP** (CSP, HSTS, etc.)
- **Validação e sanitização** de entrada de dados
- **HTTPS/TLS** para comunicação segura

Para mais detalhes, consulte o arquivo [SECURITY.md](SECURITY.md).

## Endpoints da API

A documentação interativa da API está disponível em:
- Swagger UI: https://localhost/docs
- ReDoc: https://localhost/redoc

### Principais endpoints:

- `POST /api/v1/auth/token` - Obtém token de autenticação
- `GET /api/v1/clientes/` - Lista todos os clientes (requer autenticação)
- `POST /api/v1/clientes/` - Cria um novo cliente (requer autenticação)
- `GET /api/v1/clientes/{id}` - Obtém detalhes de um cliente (requer autenticação)
- `PUT /api/v1/clientes/{id}` - Atualiza um cliente (requer autenticação)
- `DELETE /api/v1/clientes/{id}` - Remove um cliente (requer autenticação)
- `POST /api/v1/clientes/cnpj/{cnpj}` - Busca dados de um CNPJ (requer autenticação)

## Testes

### Testes Unitários

```bash
pytest tests/unit/
```

### Testes de Integração

```bash
pytest tests/integration/
```

### Testes de Segurança

```bash
# Executa verificações de segurança básicas
python security_check.py

# Executa análise estática de código
bandit -r src/
```

## Monitoramento

O projeto inclui integração com Prometheus e Grafana para monitoramento:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (usuário: admin, senha: configurada no .env)

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Implemente suas mudanças e adicione testes
4. Execute os testes para garantir que tudo está funcionando
5. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
6. Envie para o branch (`git push origin feature/nova-feature`)
7. Abra um Pull Request

## Licença
Proprietária - Todos os direitos reservados