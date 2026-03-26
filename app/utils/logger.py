import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


auth_logger = setup_logger("auth")
assets_logger = setup_logger("assets")
watchlist_logger = setup_logger("watchlist")
users_logger = setup_logger("users")
app_logger = setup_logger("app")