import logging
import structlog

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return structlog.get_logger()

logger = structlog.get_logger()