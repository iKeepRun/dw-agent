from sqlalchemy.dialects.mssql.information_schema import columns

from app.core.log import logger

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DBMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session



    async def select_column_type(self,table_name:str)-> dict[str,str]:
        sql=f'show columns from {table_name}'

        result=await self.session.execute(text(sql))
        rows = result.mappings().fetchall()

        return {row['Field']:row['Type'] for row in rows}

    async def select_example(self, column_name:str,table_name:str,limit:int=10) -> list:
        sql=f'select distinct {column_name} from {table_name} limit {limit}'

        result=await self.session.execute(text(sql))

        rows=result.mappings().fetchall()
        # 只提取值
        values=[row[column_name] for row in rows]
        # logger.info(f'values: {values}')
        return values
