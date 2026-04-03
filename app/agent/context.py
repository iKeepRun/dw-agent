from langchain_huggingface import HuggingFaceEndpointEmbeddings
from typing_extensions import TypedDict

from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.db.db_mysql_respositiry import DBMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository: ColumnQdrantRepository
    embedding_client:HuggingFaceEndpointEmbeddings
    metric_qdrant_repository:MetricQdrantRepository
    value_es_repository: ValueEsRepository
    meta_mysql_repository: MetaMysqlRepository
    db_mysql_repository:DBMysqlRepository