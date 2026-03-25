import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.client: AsyncElasticsearch | None = None
        self.ESConfig: ESConfig | None = config

    def init(self):
        self.client = AsyncElasticsearch(
            hosts=[f"http://{self.ESConfig.host}:{self.ESConfig.port}"]
        )

    async def close(self):
        await  self.client.close()



es_client_manager = ESClientManager(config=app_config.es)


if __name__ == '__main__':
    es_client_manager.init()
    client=es_client_manager.client


    async def main():
        await client.indices.create(index="my-index", body={"mappings": {"properties": {"field1": {"type": "text"}}}})
        await client.index(index="my-index", body={"field1": "some text"})
        await client.indices.refresh(index="my-index")
        result = await client.search(index="my-index", query={"match": {"field1": "some text"}})
        print(result)

        await es_client_manager.close()


    asyncio.run(main())


