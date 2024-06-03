import logging
import os

def setup_logging(config_level_name, log_path=None):
    
    if log_path is None:
        log_path = os.path.join(os.getcwd(), 'data', 'app.log')
    
    # Yeah, I know, that it looks strange, but .basicConfig not working for some reason
    # with manual handler add, it starts writing to a file.
        # Use getattr to safely get the logging level from the logging module
    # Default to logging.INFO if the specified level name is not found
    logging_level = getattr(logging, config_level_name.upper(), logging.INFO)

    logging.basicConfig(
        filename=log_path,  # Name of the file where logs will be written
        filemode='a',  # Append mode, which will append the logs to the file if it exists
        format='%(asctime)s - %(levelname)s - %(message)s',  # Format of the log messages
        level=logging_level #log level from config
    )
    logger = logging.getLogger(__name__)

    logger.setLevel(logging_level)  # Set the logger to capture INFO and higher level messages
    # Create a file handler which logs even debug messages
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging_level)  # Set the file handler to capture DEBUG and higher level messages
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(fh)


    return logger