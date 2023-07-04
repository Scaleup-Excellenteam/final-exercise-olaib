import os
import openai
import logging
import datetime
from flask import Flask
from flask.cli import load_dotenv
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
BACKUP_COUNT = 5
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
print(LOG_DIR)
APP_LOG_NAME = 'tests'

app = Flask(__name__)
app.config['SOURCES'] = os.path.join(os.path.dirname(__file__), 'sources')
# app.config['UPLOADS'] = os.path.join(os.path.dirname(__file__), 'uploads')
# app.config['OUTPUT'] = os.path.join(os.path.dirname(__file__), 'output')


def setup_logger(logger_name, log_dir):
    """
    Setup a logger for the application according to the given logger name and log directory
    :param logger_name: dir name
    :param log_dir: log dir path
    :return: logger object that can save last 5 days of logs
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file_name = f"{current_date}.log"
    log_file_path = os.path.join(log_dir, log_file_name)

    # Create the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler for the log
    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", backupCount=BACKUP_COUNT)
    file_handler.setLevel(logging.INFO)

    # Set the log format for the file handler
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger


os.makedirs(LOG_DIR, exist_ok=True)

tests_log = setup_logger(APP_LOG_NAME, LOG_DIR)
