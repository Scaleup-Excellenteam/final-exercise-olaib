from config import setup_logger, app

# Load configurations from config.py
app.config.from_object('config')

# Set up logger
setup_logger()
