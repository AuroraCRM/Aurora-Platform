# Recomendações de Melhorias de Segurança - Aurora Platform

Este documento apresenta recomendações específicas para melhorar a segurança da Aurora Platform, com base na auditoria realizada. As recomendações estão organizadas por prioridade e incluem exemplos de código para implementação.

## Melhorias de Alta Prioridade

### 1. Remover Credenciais Hardcoded

**Problema**: O arquivo `servico_crm.py` contém constantes para chaves de API que podem ser usadas para armazenar credenciais.

**Solução**: Mover todas as credenciais para variáveis de ambiente.

**Implementação**:

```python
# Antes
CNPJA_API_KEY_PRIMARY = None
CNPJA_API_KEY_SECONDARY = None

# Depois
from aurora.config import settings

# Remover as constantes e usar settings.CNPJA_PRIMARY_KEY
```

### 2. Implementar Validação Adicional de Entrada

**Problema**: Alguns endpoints podem não ter validação suficiente de entrada, especialmente para dados de clientes.

**Solução**: Adicionar validadores Pydantic mais rigorosos e validação adicional nos endpoints.

**Implementação**:

```python
# Adicionar ao arquivo cliente_schemas.py
from pydantic import BaseModel, EmailStr, validator, constr
import re

class ClienteCreate(BaseModel):
    razao_social: constr(min_length=3, max_length=100)
    nome_fantasia: Optional[constr(max_length=100)] = None
    cnpj: constr(min_length=14, max_length=18)
    inscricao_estadual: Optional[constr(max_length=20)] = None
    telefone: Optional[constr(max_length=20)] = None
    email: Optional[EmailStr] = None
    site: Optional[constr(max_length=100)] = None
    segmento: Optional[constr(max_length=50)] = None
    observacoes: Optional[str] = None