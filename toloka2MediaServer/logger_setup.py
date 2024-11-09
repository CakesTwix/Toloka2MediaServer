import logging
import os


def setup_logging(config_level_name, log_path=None):

    if log_path is None:
        log_path = os.path.join(os.getcwd(), "data", "app.log")

    # Use getattr to safely get the logging level from the logging module
    # Default to logging.INFO if the specified level name is not found
    logging_level = getattr(logging, config_level_name.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("appLogger")
    logger.setLevel(logging_level)

    # Create file handler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging_level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)

    return logger
