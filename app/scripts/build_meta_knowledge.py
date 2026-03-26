import argparse
import asyncio
import sys
from pathlib import Path

from app.core.log import logger
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(conf_path: Path):

    meta_knowledge_service = MetaKnowledgeService()
    await meta_knowledge_service.build(conf_path)


if __name__ == '__main__':
    # 构建脚本命令行参数解析器
    parse = argparse.ArgumentParser()
    # 添加命令行参数conf(元数据配置文件路径)
    parse.add_argument("-c", "--conf")
    # 生成参数对象
    args = parse.parse_args()
    # 运行构建任务
    asyncio.run(build(Path(args.conf)))
