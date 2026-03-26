from pathlib import Path

from app.core.log import logger
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig


class MetaKnowledgeService:

    async def build(self, conf_path: Path):
        # 加载元数据配置文件
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        logger.info(meta_config.metrics)

