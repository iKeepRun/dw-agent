import argparse
import asyncio
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import  meta_mysql_client_manager, db_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.db.db_mysql_respositiry import DBMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(conf_path: Path):

    # Service->repository->meta_session,->client
    #   初始化mysql客户端
    meta_mysql_client_manager.init()
    db_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    # 获取session对象
    async with meta_mysql_client_manager.session_factory() as meta_session,db_mysql_client_manager.session_factory() as db_session:
      # 构建meta_repository对象
      meta_mysql_repository = MetaMysqlRepository(meta_session)
      # 构建db_repository对象
      db_mysql_repository = DBMysqlRepository(db_session)
      # 构建column_qdrant_repository对象
      column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
      # 构建es_repository对象
      value_es_repository = ValueEsRepository(es_client_manager.client)
      # 构建metric_qdrant_repository对象
      metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)
      # 构建Service对象
      meta_knowledge_service = MetaKnowledgeService(meta_mysql_repository=meta_mysql_repository,
                                                    db_mysql_repository=db_mysql_repository,
                                                    column_qdrant_repository=column_qdrant_repository,
                                                    embedding_client=embedding_client_manager.client,
                                                    value_es_repository=value_es_repository,
                                                    metric_qdrant_repository=metric_qdrant_repository
                                                    )
      # 调用Service层的构建方法
      await meta_knowledge_service.build(conf_path)

    # 关闭连接
    await meta_mysql_client_manager.close()
    await db_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()

if __name__ == '__main__':
    # 控制台执行脚本 python -m app.scripts.build_meta_knowledge -c  conf/meta_config.yaml
    # 构建脚本命令行参数解析器
    parse = argparse.ArgumentParser()
    # 添加命令行参数conf(元数据配置文件路径)
    parse.add_argument("-c", "--conf")
    # 生成参数对象
    args = parse.parse_args()
    # 运行构建任务
    asyncio.run(build(Path(args.conf)))
