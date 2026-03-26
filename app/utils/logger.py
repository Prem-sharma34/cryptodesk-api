import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # console handler — prints to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # JSON formatter — each log line is a valid JSON object
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# module-level loggers — import these directly in other files
auth_logger = setup_logger("auth")
assets_logger = setup_logger("assets")
watchlist_logger = setup_logger("watchlist")
users_logger = setup_logger("users")
app_logger = setup_logger("app")