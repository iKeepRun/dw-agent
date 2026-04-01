from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import PointStruct

from app.conf.app_config import app_config
from app.entities.column_info import ColumnInfo
from app.core.log import logger

class ColumnQdrantRepository:
    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.qdrant_client = qdrant_client

    collection_name = "column_collections"

    async def ensure_collection(self):
        # Create a collection
        if not await self.qdrant_client.collection_exists(self.collection_name):
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=app_config.qdrant.embedding_size, distance=models.Distance.COSINE),
            )

    async def upsert(self,ids:list[str],vectors:list[list[float]],payloads:list[dict],batch_size:int=10):
        # 创建点
        points=  [ PointStruct(id=id, vector=vector, payload=payload)     for id, vector, payload in zip(ids,vectors,payloads)]
        # 批量插入
        for i in range(0,len(points),batch_size):
            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points[i:i+batch_size]
            )

    async def query_points(self, embedding_texts:list[list[float]],score_threshold=0.6,limit=5):
        column_infos_list:list[ColumnInfo]=[]
        map:dict[str,ColumnInfo]= {}
        for embedding_text in embedding_texts:
            search_results= (await  self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=embedding_text,
                with_payload=True,
                limit=limit,
                score_threshold=score_threshold
            )).points

            # 去重操作
            column_infos=[ColumnInfo(**search_result.payload) for search_result in search_results]
            col_ids=[column_info.id for column_info in column_infos]
            # logger.info(f"检索到的column_infos信息为：{col_ids}")
            for column_info in column_infos:
                if column_info.id not in map:
                    map[column_info.id]=column_info


        column_infos_list.extend(list(map.values()))
        return column_infos_list