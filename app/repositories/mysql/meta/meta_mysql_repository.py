from huggingface_hub import model_info
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import meta_mysql_client_manager
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper


class MetaMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session :AsyncSession = session

    # 这里用同步方法，因为add_all方法是同步方法
    def insert_table_info(self, table_info_list:list[TableInfo]):

       model_list=[TableInfoMapper.to_model(table_info) for table_info in table_info_list]
       self.session.add_all(model_list)

    def insert_column_info(self, column_info_list:list[ColumnInfo]):
        model_list=[ColumnInfoMapper.to_model(column_info) for column_info in column_info_list]
        self.session.add_all(model_list)

    def insert_metric_info(self, metric_info_list):
         model_list=[MetricInfoMapper.to_model(metric_info) for metric_info in metric_info_list]
         self.session.add_all(model_list)

    def insert_metric_column_info(self, column_metric_list):
        model_list=[ColumnMetricMapper.to_model(column_metric) for column_metric in column_metric_list]
        self.session.add_all(model_list)


    async def get_column_info_by_id(self, column_info_id:str) -> ColumnInfo:
       column_info_mysql:ColumnInfoMySQL= await self.session.get(ColumnInfoMySQL, column_info_id)
       return ColumnInfoMapper.to_entity(column_info_mysql)

    async def get_table_info_by_id(self, table_id:str):
        table_info_mysql: TableInfoMySQL = await self.session.get(TableInfoMySQL, table_id)
        return TableInfoMapper.to_entity(table_info_mysql)

    async def get_key_info_by_id(self, table_id:str):
        sql="select * from column_info where table_id=:table_id and role in ('primary_key','foreign_key')"
        execute=await  self.session.execute(text(sql),{'table_id':table_id})

        return [ ColumnInfo(**dict(row)) for row  in execute.mappings().fetchall()]