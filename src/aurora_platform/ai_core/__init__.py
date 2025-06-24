"""
Pacote AI Core da Aurora.

Este pacote contém os componentes fundamentais para o sistema de aprendizado
contínuo da Aurora, incluindo ingestão de dados, armazenamento de conhecimento
e feedback loop.
"""

from aurora_platform.ai_core.data_ingestion import (
    DataIngestionProcessor,
    InteractionEvent,
)
from aurora_platform.ai_core.knowledge_storage import KnowledgeStorage, KnowledgeEntry
from aurora_platform.ai_core.feedback_loop import (
    FeedbackProcessor,
    FeedbackType,
    FeedbackEntry,
)

__all__ = [
    "DataIngestionProcessor",
    "InteractionEvent",
    "KnowledgeStorage",
    "KnowledgeEntry",
    "FeedbackProcessor",
    "FeedbackType",
    "FeedbackEntry",
]
