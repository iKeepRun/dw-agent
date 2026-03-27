from pathlib import Path

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
        # 同步配置文件的表数据
        if meta_config.tables:
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

                columns_dict=await self.db_mysql_repository.select_column_type(table.name)
                # 获取每一表的字段信息-> meta数据库中columns_info表的数据，存入数据库
                for column in table.columns:
                    examples = await self.db_mysql_repository.select_example(column.name,table.name)


                    column_info = ColumnInfoMySQL(id=f'{table.name}.{column.name}',
                                                  name=column.name,
                                                  type=columns_dict[column.name],
                                                  role=column.role,
                                                  examples=examples,
                                                  description=column.description,
                                                  alias=column.alias,
                                                  table_id=table.name
                                                  )
                    column_info_list.append(column_info)
            # 插入列表数据，注意事物的管理，使用begin开启事物的自动管理
            async with self.meta_mysql_repository.session.begin():
                self.meta_mysql_repository.insert_table_info(table_info_list)
                self.meta_mysql_repository.insert_column_info(column_info_list)

            # 关闭数据库连接
            await self.db_mysql_repository.session.close()
            await self.meta_mysql_repository.session.close()
