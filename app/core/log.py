import sys
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import request_id_context_var

log_format = (
     "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
     "<level>{level: <8}</level> | "
     '<magenta>request_id -{extra[request_id]}</magenta> |'
     "<cyan>{name: <32}</cyan>:<cyan>{function:<15}</cyan>:<cyan>{line: >4}</cyan> - "
     "<level>{message}</level>"
)

logger.remove()

def inject_request_id(record):
    request_id=request_id_context_var.get()
    record["extra"]["request_id"] = request_id

logger= logger.patch(inject_request_id)

if app_config.logging.console.enable:
    logger.add(sink=sys.stdout, level=app_config.logging.console.level,format=log_format)

if app_config.logging.file.enable:
    path = Path(app_config.logging.file.path)
    path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=path / "app.log",
        rotation=app_config.logging.file.rotation,
        retention=app_config.logging.file.retention,
        level=app_config.logging.file.level,
        encoding="utf-8")



