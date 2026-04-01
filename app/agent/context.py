from langchain_huggingface import HuggingFaceEndpointEmbeddings
from typing_extensions import TypedDict

from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository: ColumnQdrantRepository
    embedding_client:HuggingFaceEndpointEmbeddings