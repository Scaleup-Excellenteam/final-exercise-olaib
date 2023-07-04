import asyncio
import glob
import json
import os
import uuid
from functools import wraps
from typing import Any
from flask import jsonify
from datetime import datetime

from Backend.config import app, app_log as log, explainer_log, NOT_FOUND, ERROR_OCCURRED, SEPERATOR \
    , JSON_FILE_EXTENSION

from models import PptxProcessor, slides_explanations_generator

from pathlib import Path


def handle_errors(func):
    """ Handle the errors decorator
    :param func: the async function to wrap
    :return: the wrapper function
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """ The wrapper function
        :param args: the arguments
        :param kwargs: the keyword arguments
        :return: the function result
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            slide_number = args[0]
            app.logger.error(f"{ERROR_OCCURRED} {slide_number}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return wrapper


def parse_pptx_to_json(file, filename: str) -> None:
    """ Parse the pptx file to json
    :param file: the pptx file
    :param filename: the name of the file
    :return: None
    """
    log.info(f'parsing <{filename}> pptx file to json')
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'])  # Get the pptx file path

    # Process the uploaded file from pptx 2 json and save it to json
    pptx_processor = PptxProcessor(file=file, file_name=filename)
    pptx_processor.save_parse_content_to_json(upload_file=uploaded_file_path)
    app.logger.info(f'File {filename} uploaded successfully')


def get_matching_files(directory, prefix: str) -> list:
    """ Get the matching files from the directory
    :param directory: the directory to search in
    :param prefix: the prefix of the file
    :return: the matching files
    """
    matching_files = [file for file in os.listdir(directory) if file.startswith(prefix)]
    return matching_files


def get_explanation(uid: str, uploaded_filename) -> Any:
    """ Get the explanation from the output file
    :param uid: the unique id of the file
    :param uploaded_filename: the name of the uploaded file
    :return: the explanation as a string or None if the file does not exist
    """
    output_dir = app.config['OUTPUT_FOLDER']
    matching_files = get_matching_files(output_dir, uid + SEPERATOR)

    if len(matching_files) == 0:
        return None

    file_path = os.path.join(output_dir, matching_files[0])
    with open(file_path, 'r') as f:
        explanation = json.load(f)
    return explanation


def get_status(uid: uuid) -> Any:
    """ Get the status of the file
    :param uid: the unique id of the file
    :return: the status of the file
    """
    upload_dir = app.config['UPLOAD_FOLDER']
    matching_files = get_matching_files(upload_dir, uid + SEPERATOR)

    if len(matching_files) == 0:
        log.info(f"File with {uid} {NOT_FOUND}")
        return jsonify({"status": NOT_FOUND}), 404

    filename = matching_files[0].split('.')[0]
    log.info(f"filename {filename} found")

    original_filename = filename.split(SEPERATOR)[1]
    log.info(f"File {original_filename} found")

    output_dir = app.config['OUTPUT_FOLDER']
    timestamp = get_upload_timestamp(filename)
    matching_files = get_matching_files(output_dir, uid + SEPERATOR)
    # Check if the file has been processed
    if len(matching_files) == 0:
        return get_upload_file_status_as_json("pending", original_filename, timestamp, None)
    uploaded_filename = matching_files[0].split('.')[0]
    log.info(f"File {uploaded_filename} found")
    # file has been processed - get the explanation

    explanation = get_explanation(uid, uploaded_filename)

    return get_upload_file_status_as_json("done", original_filename, timestamp, explanation)


def get_upload_file_status_as_json(status: str, filename: str, timestamp: str, explanation: list | None) -> dict:
    """
    Returns the status of the uploaded file as a json object
    :param status: The status of the uploaded file
    :param filename: The name of the uploaded file
    :param timestamp: The timestamp of the uploaded file
    :param explanation: The explanation of the uploaded file
    :return: The status of the uploaded file as a json object
    example:
    {
        "status": "done", # or "pending"
        "filename": "test",
        "timestamp": "2021-08-01T12:00:00",
        "explanation": [...]
    }
    """
    log.info(f"File {filename} status is {status}")
    return {
        "status": status,
        "filename": filename,
        "timestamp": timestamp,
        "explanation": explanation
    }


@handle_errors
async def explainer():
    explainer_log.info('Starting explainer loop')
    # Scan the uploads folder for new files from ../uploads
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], f"*{JSON_FILE_EXTENSION}"))
    for file in files:
        filename = Path(file).name.split('.')[0]
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}{JSON_FILE_EXTENSION}")

        # Check if the file has already been processed
        if not os.path.exists(output_filepath):
            explainer_log.info(f"Start generating explanations for file: {filename}")
            try:
                await slides_explanations_generator(file, filename)
                explainer_log.info(f"File processed successfully: {filename}")
            except Exception as e:
                explainer_log.error(f"Error processing file: {filename}: {e}")


def get_upload_timestamp(uploaded_file) -> str:
    """
    Returns the timestamp of the uploaded file from the file name (the last part of the file name)
    :param uploaded_file: The uploaded file
    :return: The timestamp of the uploaded file
    example: get_upload_timestamp("uid-test-1627814400.json") -> "2021-08-01T12:00:00"
    """
    explainer_log.info(f"Getting upload timestamp for file: {uploaded_file}")
    timestamp_str = uploaded_file.split(SEPERATOR)[-1]
    timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    return timestamp.isoformat()

#
# if __name__ == '__main__':
#     # Start the explainer loop
#     asyncio.run(explainer())
