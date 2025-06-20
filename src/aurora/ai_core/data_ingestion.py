"""
Módulo de Ingestão de Dados para o sistema de aprendizado contínuo da Aurora.

Este módulo é responsável por capturar, processar e preparar os dados de interação
do usuário para alimentar o ciclo de aprendizado contínuo da Aurora.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import re
from pydantic import BaseModel, Field


class InteractionEvent(BaseModel):
    """Modelo para eventos de interação do usuário com o sistema."""

    event_id: str = Field(..., description="Identificador único do evento")
    event_type: str = Field(
        ..., description="Tipo de evento (ex: chat, email, ticket, venda)"
    )
    source: str = Field(..., description="Origem do evento (ex: crm, chat, email)")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Data e hora do evento"
    )
    user_id: Optional[str] = Field(None, description="ID do usuário que gerou o evento")
    content: Dict[str, Any] = Field(..., description="Conteúdo do evento")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )
    entity_type: Optional[str] = Field(
        None, description="Tipo de entidade relacionada (ex: cliente, oportunidade)"
    )
    entity_id: Optional[str] = Field(None, description="ID da entidade relacionada")


class DataIngestionProcessor:
    """
    Processador de ingestão de dados para o sistema de aprendizado contínuo.

    Responsável por receber, validar, limpar e preparar os dados de interação
    para serem armazenados e utilizados no aprendizado.
    """

    def __init__(self, embedding_service=None, storage_service=None):
        """
        Inicializa o processador de ingestão de dados.

        Args:
            embedding_service: Serviço para geração de embeddings (opcional)
            storage_service: Serviço para armazenamento de dados (opcional)
        """
        self.embedding_service = embedding_service
        self.storage_service = storage_service

    def process_user_interaction_event(self, event_data: Dict[str, Any]) -> str:
        """
        Processa um evento de interação do usuário.

        Args:
            event_data: Dados do evento de interação

        Returns:
            str: ID do evento processado

        Raises:
            ValueError: Se os dados do evento forem inválidos
        """
        # Validação dos dados usando Pydantic
        try:
            event = InteractionEvent(**event_data)
        except Exception as e:
            raise ValueError(f"Dados de evento inválidos: {str(e)}")

        # Pré-processamento do conteúdo textual
        if "text" in event.content:
            event.content["text"] = self._preprocess_text(event.content["text"])

        # TODO: Integração com serviço de embeddings
        # if self.embedding_service:
        #     text_content = self._extract_text_content(event.content)
        #     embedding = self.embedding_service.generate_embedding(text_content)
        #     event.metadata["embedding"] = embedding

        # TODO: Armazenamento do evento processado
        # if self.storage_service:
        #     self.storage_service.store_event(event.dict())

        # Simulação de log para desenvolvimento
        print(f"Evento processado: {event.event_id} - {event.event_type}")

        return event.event_id

    def process_batch(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Processa um lote de eventos de interação.

        Args:
            events: Lista de eventos para processamento

        Returns:
            List[str]: Lista de IDs dos eventos processados
        """
        processed_ids = []
        for event_data in events:
            try:
                event_id = self.process_user_interaction_event(event_data)
                processed_ids.append(event_id)
            except Exception as e:
                print(f"Erro ao processar evento: {str(e)}")

        return processed_ids

    def _preprocess_text(self, text: str) -> str:
        """
        Realiza pré-processamento básico em texto.

        Args:
            text: Texto a ser processado

        Returns:
            str: Texto processado
        """
        if not text:
            return ""

        # Normalização básica
        text = text.strip()

        # Remove caracteres especiais e mantém apenas um espaço entre palavras
        text = re.sub(r"\s+", " ", text)

        # TODO: Implementar normalização mais avançada:
        # - Remoção de stopwords
        # - Lematização/Stemming
        # - Normalização de entidades nomeadas

        return text

    def _extract_text_content(self, content: Dict[str, Any]) -> str:
        """
        Extrai conteúdo textual de um dicionário de conteúdo.

        Args:
            content: Dicionário com o conteúdo do evento

        Returns:
            str: Conteúdo textual extraído
        """
        text_parts = []

        # Extrai texto de diferentes campos possíveis
        if "text" in content:
            text_parts.append(content["text"])
        if "subject" in content:
            text_parts.append(content["subject"])
        if "description" in content:
            text_parts.append(content["description"])

        return " ".join(text_parts)


# Exemplo de integração com o CRM
def register_crm_hooks():
    """
    Registra hooks para capturar eventos do CRM.

    TODO: Implementar integração real com os serviços do CRM.
    """
    # Exemplo de como seria a integração com ClienteService
    # from aurora.services.cliente_service import ClienteService
    #
    # # Monkey patch ou decorador para capturar eventos
    # original_create_cliente = ClienteService.create_cliente
    #
    # def create_cliente_with_event_capture(self, cliente_data):
    #     result = original_create_cliente(self, cliente_data)
    #
    #     # Captura o evento para aprendizado
    #     event_data = {
    #         "event_id": f"cliente_create_{result['id']}",
    #         "event_type": "cliente_create",
    #         "source": "crm",
    #         "content": cliente_data,
    #         "entity_type": "cliente",
    #         "entity_id": str(result['id'])
    #     }
    #
    #     # Processamento assíncrono do evento
    #     # asyncio.create_task(process_event_async(event_data))
    #
    #     return result
    #
    # ClienteService.create_cliente = create_cliente_with_event_capture
    pass
