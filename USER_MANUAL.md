# Manual Técnico - Aurora Platform

## 1. Visão Geral do Sistema

A Aurora Platform é um sistema de CRM (Customer Relationship Management) desenvolvido para gerenciar relacionamentos com clientes, automatizar processos de vendas e fornecer insights de negócios. O sistema é construído com uma arquitetura moderna, utilizando FastAPI como framework principal, SQLAlchemy para ORM, e diversos componentes para garantir segurança, desempenho e escalabilidade.

### 1.1 Componentes Principais

- **API RESTful**: Interface principal para interação com o sistema
- **Banco de Dados**: PostgreSQL para armazenamento persistente
- **Cache**: Redis para armazenamento em cache
- **Autenticação**: Sistema JWT com suporte a 2FA
- **Integração Externa**: API CNPJá para consulta de dados de empresas
- **Monitoramento**: Prometheus e Grafana
- **Segurança**: ModSecurity como WAF

### 1.2 Arquitetura

A Aurora Platform segue uma arquitetura em camadas:

1. **Camada de Apresentação**: API RESTful (FastAPI)
2. **Camada de Serviço**: Lógica de negócio
3. **Camada de Repositório**: Acesso a dados
4. **Camada de Modelo**: Entidades de domínio
5. **Camada de Infraestrutura**: Banco de dados, cache, etc.

Além disso, o sistema inclui um módulo de IA (ai_core) para aprendizado contínuo e personalização proativa.

## 2. Requisitos do Sistema

### 2.1 Requisitos de Software

- Python 3.8 ou superior
- Docker e Docker Compose
- PostgreSQL 15
- Redis 7
- Nginx com ModSecurity

### 2.2 Requisitos de Hardware (Mínimo)

- CPU: 2 cores
- RAM: 4 GB
- Armazenamento: 20 GB

## 3. Instalação e Configuração

### 3.1 Instalação Local para Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Aurora-Platform.git
   cd Aurora-Platform
Crie e ative um ambiente virtual:

bash
Copiar
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate    # Windows
Instale as dependências:

bash
Copiar
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento
Configure o arquivo .env:

bash
Copiar
# Copie o arquivo de exemplo
cp .env.example .env
# Edite o arquivo com suas configurações
Execute as migrações do banco de dados:

bash
Copiar
python src/aurora/init_db.py
Inicie o servidor de desenvolvimento:

bash
Copiar
python run_api.py
3.2 Implantação com Docker
Configure o arquivo .env para produção

Construa e inicie os contêineres:

bash
Copiar
docker-compose up -d
Verifique se todos os serviços estão em execução:

bash
Copiar
docker-compose ps
4. Estrutura do Projeto
bash
Copiar
Aurora-Platform/
├── src/
│   └── aurora/
│       ├── ai_core/           # Módulo de IA e aprendizado contínuo
│       ├── auth/              # Autenticação e segurança
│       ├── cache/             # Serviços de cache
│       ├── integrations/      # Integrações externas
│       ├── middleware/        # Middlewares FastAPI
│       ├── models/            # Modelos SQLAlchemy
│       ├── repositories/      # Repositórios de dados
│       ├── routers/           # Rotas da API
│       ├── schemas/           # Schemas Pydantic
│       ├── services/          # Serviços de negócio
│       └── utils/             # Utilitários
├── tests/                     # Testes automatizados
├── security/                  # Ferramentas e configurações de segurança
└── assets/                    # Recursos estáticos
5. Componentes Principais
5.1 API RESTful (FastAPI)
A API é o ponto de entrada principal para o sistema, fornecendo endpoints para todas as funcionalidades. Os principais endpoints incluem:

/api/v1/auth: Autenticação e gerenciamento de usuários

/api/v1/clientes: Gerenciamento de clientes

/api/v1/cnpj: Consulta de dados de CNPJ

/api/v1/admin: Operações administrativas (requer 2FA)

5.2 Banco de Dados
O sistema utiliza PostgreSQL como banco de dados principal, com SQLAlchemy como ORM. As principais entidades incluem:

ClienteDB: Informações de clientes

LeadDB: Leads de vendas

5.3 Autenticação e Segurança
O sistema implementa várias camadas de segurança:

JWT: Tokens de acesso seguros

2FA: Autenticação de dois fatores

Rate Limiting: Proteção contra força bruta

Cabeçalhos de Segurança: Proteção contra ataques web comuns

ModSecurity: WAF para proteção adicional

5.4 Módulo de IA (ai_core)
O módulo de IA implementa aprendizado contínuo com três componentes principais:

Ingestão de Dados: Captura e processamento de interações

Armazenamento de Conhecimento: Armazenamento vetorial para RAG

Feedback Loop: Captura e aplicação de feedback para melhoria contínua

6. Fluxos de Trabalho Principais
6.1 Cadastro de Cliente
O usuário envia dados do cliente via API

O sistema valida os dados

O sistema verifica duplicidade de CNPJ

O cliente é criado no banco de dados

O sistema retorna os dados do cliente criado

6.2 Consulta de CNPJ
O usuário envia um CNPJ para consulta

O sistema verifica o cache

Se não estiver em cache, consulta a API externa

Os dados são processados e retornados

Os dados são armazenados em cache para consultas futuras

6.3 Autenticação de Usuário
O usuário envia credenciais

O sistema valida as credenciais

Se 2FA estiver ativado, solicita código

O sistema gera e retorna um token JWT

O token é usado para autenticar requisições subsequentes

7. Configuração e Personalização
7.1 Variáveis de Ambiente
As principais variáveis de ambiente incluem:

DATABASE_URL: URL de conexão com o banco de dados

SECRET_KEY: Chave secreta para JWT

ALGORITHM: Algoritmo para JWT (HS256 recomendado)

ACCESS_TOKEN_EXPIRE_MINUTES: Tempo de expiração do token

CNPJA_PAID_URL: URL da API paga da CNPJá

CNPJA_FREE_URL: URL da API gratuita de fallback

CNPJA_PRIMARY_KEY: Chave primária da API CNPJá

CNPJA_SECONDARY_KEY: Chave secundária da API CNPJá

CNPJA_AUTH_TYPE: Tipo de autenticação (ex: Bearer)

7.2 Configuração do Docker
O arquivo docker-compose.yml define os serviços necessários para a aplicação. Você pode ajustar:

Limites de recursos (CPU, memória)

Portas expostas

Volumes persistentes

Configurações de rede

8. Monitoramento e Logs
8.1 Logs
Os logs são configurados para fornecer informações detalhadas sobre o funcionamento do sistema:

Logs de aplicação: /app/logs

Logs do Nginx: /var/log/nginx

Logs do ModSecurity: /var/log/modsecurity

8.2 Monitoramento
O sistema utiliza Prometheus e Grafana para monitoramento:

Prometheus: Coleta métricas

Grafana: Visualização de métricas e dashboards

Acesse o Grafana em http://localhost:3000 com as credenciais configuradas.

9. Solução de Problemas
9.1 Problemas Comuns
Problema	Possível Causa	Solução
API não inicia	Configuração incorreta do banco de dados	Verifique as variáveis de ambiente e a conexão com o banco
Erro de autenticação	Token expirado ou inválido	Gere um novo token de acesso
Lentidão nas consultas	Cache não configurado corretamente	Verifique a conexão com o Redis
Erro na consulta de CNPJ	API externa indisponível	Verifique a chave da API e a disponibilidade do serviço

9.2 Logs de Erro
Os logs de erro são armazenados em /app/logs/error.log. Consulte este arquivo para informações detalhadas sobre erros.

10. Segurança
10.1 Melhores Práticas
Mantenha todas as dependências atualizadas

Não armazene segredos no código-fonte

Utilize HTTPS em produção

Implemente o princípio do menor privilégio

Realize backups regulares do banco de dados

10.2 Atualizações de Segurança
Verifique regularmente por atualizações de segurança:

bash
Copiar
pip install safety
safety check
11. Desenvolvimento e Contribuição
11.1 Ambiente de Desenvolvimento
Configure o ambiente conforme a seção 3.1

Instale as dependências de desenvolvimento:

bash
Copiar
pip install -r requirements-dev.txt
11.2 Testes
Execute os testes automatizados:

bash
Copiar
pytest
11.3 Padrões de Código
O projeto segue os seguintes padrões:

PEP 8 para estilo de código

Docstrings para documentação

Type hints para tipagem estática

Testes unitários para funcionalidades críticas

12. Referências
FastAPI Documentation

SQLAlchemy Documentation

OWASP Top 10

Docker Documentation

Versão do Manual: 1.0.0

Data de Atualização: [21/06/2025]