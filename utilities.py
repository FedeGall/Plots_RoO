import logging

from pathlib import Path

def logs(file_name, logger_name):
    logs_folder = Path("logs")   # Create Path object to folder with logs
    logger = logging.getLogger(f"{logger_name}")   # Add logger
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")    # Formatting for the log message
    fileHandler = logging.FileHandler(logs_folder / f'{file_name}.log', mode='a')     # File to use as log
    fileHandler.setFormatter(formatter)     # Set for that file the formatting of the messages
    logger.setLevel(logging.INFO)   # Use info as level for the log
    logger.addHandler(fileHandler)  # Add handler to the logger
    return logger
