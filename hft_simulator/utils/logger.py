import logging
from config import LOG_LEVEL, LOG_FORMAT # In a real project

def setup_logger(name: str) -> logging.Logger:
    """Sets up a configured logger instance."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger