import os
import openai
import logging
import datetime
from flask import Flask
from flask.cli import load_dotenv
from logging.handlers import TimedRotatingFileHandler

load_dotenv()

# Constants
ROLE = "user"
PROCESS_INTERVAL = 10  # seconds for explanation generation
GENERATION_TIMEOUT = 10
ERROR_OCCURRED_MESSAGE = "An error occurred while processing the presentation:"
RATE_LIMIT_SECONDS = 1
WAIT_TIME = 60
RATE_LIMIT_MSG = f"Rate limit exceeded. Please wait {WAIT_TIME} seconds and try again."
VALID_FORMATS = ('pptx', 'ppt')
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
UNSELECTED_FILE = 'No file selected'
FILE_NOT_SUPPORTED = 'Only pptx files are supported'
NOT_FOUND = 'Not found'
ERROR_OCCURRED = 'An error occurred while processing the presentation:'
SEPERATOR = '/'
JSON_FILE_EXTENSION = '.json'
EXPLAINER_INTERVAL = 10
# OpenAI Configuration
OPEN_AI_MODEL = os.environ.get('OPEN_AI_MODEL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')
WAIT_TIME = 60
# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = "logs"
EXPLAINER_LOG_NAME = "explainer"
APP_LOG_NAME = "app"
BACKUP_COUNT = 5

# Set Flask app configurations
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = os.path.join(app.root_path, OUTPUT_FOLDER)
openai.api_key = OPEN_AI_API_KEY


def setup_logger(logger_name, log_dir):
    """
    Setup a logger for the application according to the given logger name and log directory
    :param logger_name: dir name
    :param log_dir: log dir path
    :return: logger object that can save last 5 days of logs
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

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


explainer_log = setup_logger(EXPLAINER_LOG_NAME, os.path.join(LOG_DIR, EXPLAINER_LOG_NAME))
explainer_log.info("Explainer logger initialized")
app_log = setup_logger(APP_LOG_NAME, os.path.join(LOG_DIR, APP_LOG_NAME))
