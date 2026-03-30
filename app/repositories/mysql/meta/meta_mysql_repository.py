from huggingface_hub import model_info
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import meta_mysql_client_manager
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
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