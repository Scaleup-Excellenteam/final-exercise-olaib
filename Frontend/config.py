import os
import logging
from datetime import datetime

DONE = "done"
URL = "http://localhost:5000"
UPLOAD_URL = f"{URL}/upload"
GET_STATUS_URL = f"{URL}/status"
UID_PARAM = "uid"
STATUS_PARAM = "status"
FILENAME_PARAM = "filename"
TIMESTAMP_PARAM = "timestamp"
EXPLANATION_PARAM = "explanation"
LOGS_DIR = 'logs'
EXPLANATIONS_DIR = "explanations"
TESTS_LOG_NAME = "tests"
CLIENT_LOG_NAME = "client"
INTERVAL_BETWEEN_STATUS_CHECKS = 5  # seconds between each status check

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
BACKUP_COUNT = 5


def setup_logger(logger_name: str, log_dir: str) -> logging.Logger:
    """
    Setup a logger for the application with a timestamp in the log file name
    :param logger_name: name of the logger
    :param log_dir: directory to save the log file in
    :return: logger object
    """
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"{log_dir}/{logger_name}_{current_timestamp}.log"

    # Create the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Create a file handler for the log
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)

    # Set the log format for the file handler
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger


if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
tests_log = setup_logger(TESTS_LOG_NAME, LOGS_DIR)

client_log = setup_logger(CLIENT_LOG_NAME, LOGS_DIR)
