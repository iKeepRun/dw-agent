from pathlib import Path

from app.core.log import logger
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repository: MetaMysqlRepository):
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository


    async def build(self, conf_path: Path):
        # 加载元数据配置文件
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        logger.info(meta_config.metrics)

        for table in meta_config.tables:
            # 获取每一张表数据-> meta数据库中table_info表的数据，存入数据库

            # 获取每一表的字段信息-> meta数据库中columns_info表的数据，存入数据库
            for column in table.columns:
                pass
