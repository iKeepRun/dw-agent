from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import app_config


class ColumnQdrantRepository:
    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.qdrant_client = qdrant_client

    collection_name = "column_collections"

    async def ensure_collection(self):
        # Create a collection
        if not await self.qdrant_client.collection_exists(self.collection_name):
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=app_config.qdrant.vector_size, distance=models.Distance.COSINE),
            )

    async def upsert(self,ids:list[str],vectors:list[list[float]],payloads:dict):
        await self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(id=id, vector=vector, payload=payload)
                for id, vector, payload in zip(ids, vectors, payloads)
            ],
        )
