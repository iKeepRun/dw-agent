import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    def __init__(self, config: DBConfig):
        self.config: DBConfig = config
        self.client: AsyncEngine | None = None

    def init(self):
        self.client = create_async_engine(
            f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4")

    async def close(self):
        await self.client.dispose()


db_mysql_client_manager = MysqlClientManager(config=app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(config=app_config.db_meta)

if __name__ == '__main__':
    db_mysql_client_manager.init()
    engine = db_mysql_client_manager.client


    async def main():
        async  with AsyncSession(engine) as session:
            sql = "select * from fact_order limit 10"
            result = await  session.execute(text(sql))

            rows = result.fetchall()

            print(rows[0])


    asyncio.run(main())
