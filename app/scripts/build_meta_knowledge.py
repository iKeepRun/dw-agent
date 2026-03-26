import argparse
import asyncio
import sys
from pathlib import Path

from app.clients.mysql_client_manager import MysqlClientManager, meta_mysql_client_manager
from app.core.log import logger
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(conf_path: Path):

    # Service->repository->session->client
    #   初始化mysql客户端
    meta_mysql_client_manager.init()
    # 获取session对象
    async with meta_mysql_client_manager.session_factory() as session:
      # 构建repository对象
      meta_mysql_repository = MetaMysqlRepository(session)
      # 构建Service对象
      meta_knowledge_service = MetaKnowledgeService(meta_mysql_repository)
      # 调用Service层的构建方法
      await meta_knowledge_service.build(conf_path)
    # 关闭mysql连接
    await meta_mysql_client_manager.close()

if __name__ == '__main__':
    # 构建脚本命令行参数解析器
    parse = argparse.ArgumentParser()
    # 添加命令行参数conf(元数据配置文件路径)
    parse.add_argument("-c", "--conf")
    # 生成参数对象
    args = parse.parse_args()
    # 运行构建任务
    asyncio.run(build(Path(args.conf)))
