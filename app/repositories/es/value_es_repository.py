from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.entities.value_info import ValueInfo


class ValueEsRepository:
    def __init__(self, client: AsyncElasticsearch):
        self.client:AsyncElasticsearch=client
    index_name="value_index"


    # 创建索引
    async def ensure_index(self):
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(index=self.index_name)

    async def index(self, values_infos:list[ValueInfo], batch_size:int=10):
        for i in range(0,len(values_infos),batch_size):
            batch=values_infos[i:i+batch_size]
            batch_operations=[]
            for value_info in batch:
                batch_operations.append({"index": {"_index": self.index_name}})
                batch_operations.append(asdict(value_info))



            await self.client.bulk(
                index=self.index_name,
                operations=batch_operations
            )

    async def select(self, result,min_score=0.6,limit=5):
        res=await self.client.search(
            index=self.index_name,
            query={
                "match": {
                    "value": result
                }
            },
            min_score=min_score,
            size=limit
        )
        
        return  [ValueInfo(**r['_source']) for r in res['hits']['hits']]