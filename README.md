![Tests](https://github.com/AuroraCRM/Aurora-Core/actions/workflows/tests.yml/badge.svg)


## Sobre o Projeto
Aurora é uma plataforma de CRM inteligente que atua como assistente de IA, auxiliando empresas na gestão de clientes e na automação de processos.

## Arquitetura Tecnológica
- **FastAPI** para a construção das APIs.
- **PostgreSQL** como banco de dados principal.
- **Redis** utilizado para cache e filas.
- **Docker** para orquestração e empacotamento dos serviços.

## Como Começar
1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd Aurora-Platform
   ```
2. Copie o arquivo de exemplo e configure suas variáveis de ambiente:
   ```bash
   cp .env.example .env
   # edite o .env conforme necessário
   ```
3. Suba os serviços com Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Executando os Testes
Execute todos os testes com:
```bash
pytest
```
