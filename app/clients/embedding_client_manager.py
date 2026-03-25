import asyncio

from app.conf.app_config import EmbeddingConfig, app_config
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config: EmbeddingConfig = config
        self.client: HuggingFaceEndpointEmbeddings | None = None


    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(
            model=f"http://{self.config.host}:{self.config.port}"
        )


embedding_client_manager = EmbeddingClientManager(config=app_config.embedding)




if __name__ == '__main__':
    embedding_client_manager.init()
    client=embedding_client_manager.client

    async def main():
        embeddings = await client.aembed_query("What would be a good company name for a company that makes colorful socks?")
        print(embeddings[:3])


    asyncio.run(main())