# Aurora-Platform
*O Backend Inteligente do Ecossistema Aurora*

---

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12">
  <a href="https://github.com/AuroraCRM/Aurora-Platform/actions/workflows/security-checks.yml">
    <img src="https://github.com/AuroraCRM/Aurora-Platform/actions/workflows/security-checks.yml/badge.svg" alt="Status do Build">
  </a>
  <a href="https://codecov.io/gh/AuroraCRM/Aurora-Platform">
    <img src="https://img.shields.io/codecov/c/github/AuroraCRM/Aurora-Platform" alt="Cobertura de Testes"/>
  </a>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</p>

---

## 📖 Visão Geral

**Aurora-Platform** é o coração do ecossistema Aurora. Trata-se de uma API RESTful robusta e escalável, construída com FastAPI, que serve como um CRM inteligente. A plataforma foi projetada para gerenciar clientes, automatizar processos e, principalmente, integrar capacidades de Inteligência Artificial para otimizar a tomada de decisões.

O sistema conta com um **AI Core** que permite aprendizado contínuo, uma **Base de Conhecimento Vetorial** para buscas semânticas (RAG), e integrações com modelos de linguagem como o **Microsoft Phi-3** para tarefas de classificação e geração de código.

## ✨ Estrutura da API

A API é organizada de forma modular para facilitar a manutenção e escalabilidade.

| Roteador                 | Prefixo                | Descrição                                                              |
| ------------------------ | ---------------------- | ---------------------------------------------------------------------- |
| **Autenticação**         | `/auth`                | Gerencia login, tokens (JWT), e segurança de acesso.                   |
| **Clientes e Leads**     | `/clientes`, `/leads`  | Endpoints para operações de CRUD no CRM.                               |
| **Integrações**          | `/integracoes`         | Conecta-se a serviços externos, como a API de consulta de CNPJ.        |
| **IA Services (v1)**     | `/api/v1`              | Endpoints para Code Assistance, Knowledge Base e inferência de modelos. |

## 🛠️ Stack Tecnológica

A plataforma é construída com um conjunto de tecnologias modernas e eficientes:

- **Linguagem:** Python 3.12
- **Framework API:** FastAPI
- **Banco de Dados:** PostgreSQL (produção) e SQLite (desenvolvimento/testes)
- **ORM:** SQLModel (combina SQLAlchemy e Pydantic)
- **Validação de Dados:** Pydantic
- **Gerenciador de Dependências:** Poetry
- **Testes:** Pytest
- **Cache & Filas:** Redis
- **Containerização:** Docker

## 🚀 Começando (Instalação Local)

Siga estes passos para configurar o ambiente de desenvolvimento em sua máquina local.

### Pré-requisitos

- **Git:** Para clonar o repositório.
- **pyenv:** Para gerenciar a versão do Python.
- **Poetry:** Para gerenciar as dependências do projeto.

### Guia de Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/AuroraCRM/Aurora-Platform.git
    cd Aurora-Platform
    ```

2.  **Configure a versão do Python com `pyenv`:**
    O projeto utiliza Python 3.12. Use `pyenv` para instalar e definir a versão localmente.
    ```bash
    pyenv install 3.12.3 # Ou a versão especificada em .python-version
    pyenv local 3.12.3
    ```

3.  **Instale as dependências com `Poetry`:**
    Poetry irá criar um ambiente virtual e instalar todos os pacotes necessários definidos no `pyproject.toml`.
    ```bash
    poetry install
    ```

## ⚙️ Configuração do Ambiente

A aplicação utiliza variáveis de ambiente para configurações sensíveis e específicas do ambiente.

1.  **Crie seu arquivo `.env`:**
    Copie o arquivo de exemplo para criar sua configuração local.

    ```bash
    cp .env.example .env
    ```

2.  **Edite o arquivo `.env`:**
    Abra o arquivo `.env` e ajuste as variáveis. As mais importantes são:
    - `DATABASE_URL`: String de conexão para o banco de dados principal.
    - `SECRET_KEY`: Chave secreta para a assinatura de tokens JWT.
    - `REDIS_URL`: URL para o servidor Redis, usado para cache.
    - `PHI3_MODEL_NAME`: Define qual modelo da família Phi-3 será carregado localmente.

## ▶️ Rodando a Aplicação

Com o ambiente configurado, inicie o servidor de desenvolvimento com o Uvicorn. O Poetry garantirá que o comando seja executado no ambiente virtual correto.

```bash
poetry run uvicorn src.aurora_platform.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000` e a documentação interativa em `http://127.0.0.1:8000/docs`.

## 🧪 Rodando os Testes

Para garantir a qualidade e a estabilidade do código, execute a suíte de testes completa com o Pytest.

```bash
poetry run pytest
```

## 🐳 Usando com Docker

Como alternativa à configuração local, você pode subir toda a stack (API, Banco de Dados, Redis) utilizando Docker Compose.

1.  **Configure o `.env`** conforme o passo anterior.
2.  **Suba os serviços:**
    ```bash
    docker-compose up -d
    ```

## 🤝 Como Contribuir

Agradecemos por seu interesse em contribuir com a Aurora-Platform! Para manter o projeto organizado, pedimos que siga algumas diretrizes:

1.  **Issues e Pull Requests:** Sinta-se à vontade para abrir *issues* para relatar bugs ou sugerir novas funcionalidades. Se desejar implementar uma mudança, por favor, abra um *Pull Request*.
2.  **Commits Convencionais:** Utilizamos o padrão de Conventional Commits para as mensagens de commit. Isso nos ajuda a automatizar o versionamento e a gerar changelogs.
    - `feat:` para novas funcionalidades.
    - `fix:` para correções de bugs.
    - `docs:` para mudanças na documentação.
    - `style:` para formatação de código (espaços, ponto e vírgula, etc.).
    - `refactor:` para refatorações que não alteram a funcionalidade.
    - `test:` para adição ou correção de testes.
    - `chore:` para tarefas de build, configuração, etc.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
