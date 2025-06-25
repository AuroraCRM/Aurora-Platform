from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, JSON  # Para campos JSON

# Placeholder para o modelo AIInteractionLog
# A definição exata (campos, tipos) precisa ser fornecida conforme "o modelo que definimos".


class AIInteractionLog(SQLModel, table=True):
    __tablename__ = "ai_interaction_logs"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user_id: Optional[str] = Field(
        default=None, index=True
    )  # Ou Optional[int] se FK para tabela de usuários
    session_id: Optional[str] = Field(default=None, index=True)

    interaction_type: str = Field(
        nullable=False, index=True
    )  # Ex: "code_assist_request", "general_query"

    input_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # O que o usuário enviou
    output_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # O que a IA respondeu

    log_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # Renomeado de 'metadata'

    # Adicionar mais campos conforme necessário:
    # - success: bool
    # - error_message: Optional[str]
    # - duration_ms: Optional[int]
    # - feedback_score: Optional[int] (se houver feedback do usuário)

    # Exemplo de como poderia ser usado:
    # log_entry = AIInteractionLog(
    #     user_id="user123",
    #     interaction_type="code_generation",
    #     input_data={"prompt": "generate a python function to sort a list"},
    #     output_data={"code": "def sort_list(l): return sorted(l)"},
    #     metadata={"model_name": "gpt-4", "tokens_used": 150}
    # )
