import argparse
import asyncio
import sys
from pathlib import Path

from app.core.log import logger

async def build(conf_path: Path):
    logger.info(f"元知识库配置文件：{conf_path}")







if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument("-c", "--conf")

    args = parse.parse_args()

    asyncio.run(build(Path(args.conf)))