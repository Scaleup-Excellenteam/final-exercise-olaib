import os

from config import setup_logger, app

# Load configurations from config.py
app.config.from_object('config')


def create_folder_if_not_exists(folder_path: str) -> None:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


# Create folder for uploads if not exists
create_folder_if_not_exists(app.config['UPLOAD_FOLDER'])

# Create folder for outputs if not exists
create_folder_if_not_exists(app.config['OUTPUT_FOLDER'])
