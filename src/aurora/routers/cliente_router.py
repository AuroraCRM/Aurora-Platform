# src/aurora/routers/cliente_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

# Importando os schemas Pydantic para validação e resposta
from aurora.schemas.cliente_schemas import Cliente, ClienteCreate, ClienteUpdate

# Importando a camada de serviço que contém a lógica de negócio
from aurora.services.servico_crm import ServicoCRM as ClienteService

# --- CORREÇÃO ---
# A exceção customizada é importada do módulo de utilitários, não do serviço.
from aurora.utils.exceptions import CRMServiceError

# Importando dependências para autenticação (exemplo)
# from aurora.security import get_current_active_user 

router = APIRouter()

# Exemplo de dependência de autenticação que pode ser adicionada a cada rota
# auth_dependency = Depends(get_current_active_user)

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate, 
    service: ClienteService = Depends()
    # , current_user: dict = auth_dependency # Descomente para proteger a rota
):
    """
    Cria um novo cliente no banco de dados.

    - **cliente**: Dados do cliente a ser criado, validados pelo schema ClienteCreate.
    - Retorna o cliente recém-criado.
    """
    try:
        return service.create_cliente(cliente_data=cliente)
    except CRMServiceError as e:
        # Se o serviço levantar um erro (ex: CNPJ já existe), repassa como HTTPException
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[Cliente])
def listar_clientes(
    skip: int = 0, 
    limit: int = 100, 
    service: ClienteService = Depends()
    # , current_user: dict = auth_dependency # Descomente para proteger a rota
):
    """
    Lista todos os clientes com suporte a paginação.

    - **skip**: Número de registros a pular.
    - **limit**: Número máximo de registros a retornar.
    - Retorna uma lista de clientes.
    """
    return service.get_all_clientes(skip=skip, limit=limit)


@router.get("/{cliente_id}", response_model=Cliente)
def obter_cliente(
    cliente_id: int, 
    service: ClienteService = Depends()
    # , current_user: dict = auth_dependency # Descomente para proteger a rota
):
    """
    Obtém os detalhes de um cliente específico pelo seu ID.

    - **cliente_id**: O ID do cliente a ser buscado.
    - Retorna os dados do cliente ou um erro 404 se não for encontrado.
    """
    try:
        db_cliente = service.get_cliente_by_id(cliente_id=cliente_id)
        return db_cliente
    except CRMServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{cliente_id}", response_model=Cliente)
def atualizar_cliente(
    cliente_id: int, 
    cliente_update: ClienteUpdate, 
    service: ClienteService = Depends()
    # , current_user: dict = auth_dependency # Descomente para proteger a rota
):
    """
    Atualiza um cliente existente no banco de dados.

    - **cliente_id**: O ID do cliente a ser atualizado.
    - **cliente_update**: Os campos a serem atualizados.
    - Retorna o cliente com os dados atualizados.
    """
    try:
        return service.update_cliente(cliente_id=cliente_id, cliente_data=cliente_update)
    except CRMServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(
    cliente_id: int, 
    service: ClienteService = Depends()
    # , current_user: dict = auth_dependency # Descomente para proteger a rota
):
    """
    Deleta um cliente do banco de dados.

    - **cliente_id**: O ID do cliente a ser deletado.
    - Retorna uma resposta 204 No Content em caso de sucesso.
    """
    try:
        service.delete_cliente(cliente_id=cliente_id)
        # Nenhum corpo de resposta é retornado para o status 204
        return None
    except CRMServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
