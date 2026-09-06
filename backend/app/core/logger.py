from loguru import logger
import sys
import os

os.makedirs("logs", exist_ok=True)

logger.remove()

# Console logs
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "{message}",
)

# File logs
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

app_logger = logger