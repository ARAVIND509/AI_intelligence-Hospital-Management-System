from loguru import logger
import sys
import os
from app.core.config import settings

os.makedirs("logs", exist_ok=True)

logger.remove()

log_level = getattr(settings, "LOG_LEVEL", "INFO")

# Console logs
logger.add(
    sys.stdout,
    level=log_level,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "{message}",
)

# File logs
logger.add(
    "logs/app.log",
    level=log_level,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=getattr(settings, "DEBUG", False),
    diagnose=getattr(settings, "DEBUG", False),
)

app_logger = logger