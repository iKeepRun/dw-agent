from pathlib import Path

from app.core.log import logger
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.db.db_mysql_respositiry import DBMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repository: MetaMysqlRepository,db_mysql_repository: DBMysqlRepository):
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository
        self.db_mysql_repository: DBMysqlRepository = db_mysql_repository



    #构建方法
    async def build(self, conf_path: Path):
        # 加载元数据配置文件
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        # logger.info(meta_config.metrics)

        # 申明更新数据
        table_info_list: list[TableInfoMySQL] = []
        column_info_list: list[ColumnInfoMySQL] = []

        for table in meta_config.tables:
            # 获取每一张表数据-> meta数据库中table_info表的数据，存入数据库
            table_info= TableInfoMySQL(id=table.name,
                                       name=table.name,
                                       role=table.role,
                                       description=table.description
                                       )
            table_info_list.append(table_info)

            await self.db_mysql_repository.selectColumns(table.name)
            # 获取每一表的字段信息-> meta数据库中columns_info表的数据，存入数据库
            for column in table.columns:
                column_info = ColumnInfoMySQL(id=table.name + column.name,
                                              name=column.name,
                                              type=None,
                                              role=column.role,
                                              examples=None,
                                              description=column.description,
                                              table_id=table.name
                                              )
                column_info_list.append(column_info)
