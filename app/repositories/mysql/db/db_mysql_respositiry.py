from app.core.log import logger

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DBMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session



    async def selectColumns(self,table_name:str):
        logger.info(f'table name: {table_name}')

        sql=f'show columns from {table_name}'

        result=await self.session.execute(text(sql))
        rows = result.fetchall()
        logger.info(rows[0])
        # logger.info(type(rows))
