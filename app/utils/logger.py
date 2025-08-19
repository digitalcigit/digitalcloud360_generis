import logging
import structlog

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = structlog.get_logger()
    return logger