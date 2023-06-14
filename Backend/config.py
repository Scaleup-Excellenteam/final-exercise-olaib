import os
import logging

import openai
from flask import Flask
from flask.cli import load_dotenv
from logging.handlers import TimedRotatingFileHandler

load_dotenv()
# Constants
ROLE = "user"
GENERATION_TIMEOUT = 10
ERROR_OCCURRED_MESSAGE = "An error occurred while processing the presentation:"
RATE_LIMIT_SECONDS = 1
WAIT_TIME = 60
RATE_LIMIT_MSG = f"Rate limit exceeded. Please wait {WAIT_TIME} seconds and try again."
VALID_FORMATS = ('pptx', 'ppt')
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
UNSELECTED_FILE= 'No file selected'
FILE_NOT_SUPPORTED = 'Only pptx files are supported'

# OpenAI Configuration
OPEN_AI_MODEL = os.environ.get('OPEN_AI_MODEL')
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIR, "info.log")

# Set Flask app configurations
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
openai.api_key = OPEN_AI_API_KEY


def setup_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler to save the last 5 logs
    file_handler = TimedRotatingFileHandler(LOG_FILE_PATH, when="midnight", backupCount=5)
    file_handler.setLevel(logging.INFO)

    # Set the log format for the file handler
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)


setup_logger()
logger = logging.getLogger(__name__)
