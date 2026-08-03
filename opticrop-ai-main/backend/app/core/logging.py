import logging
import os
import sys
from app.core.config import settings


def setup_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, "app.log")

    log_format = (
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s"
    )

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path, encoding="utf-8"),
        ],
        force=True,  # Overwrites existing config
    )

    logging.getLogger("uvicorn.access").handlers = []  # redirect uvicorn loggers if needed
    logging.getLogger("uvicorn.error").handlers = []

    logger = logging.getLogger("app")
    logger.info("Logging system initialized successfully. Log level: %s", settings.LOG_LEVEL)
