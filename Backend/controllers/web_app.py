import os
import uuid
from datetime import datetime
from functools import wraps
import asyncio

from flask import Blueprint, request, jsonify

from .explainer import get_status, parse_pptx_to_json
from config import VALID_FORMATS, app_log as log, app, FILE_NOT_SUPPORTED, UNSELECTED_FILE

web_app_bp = Blueprint("app", __name__)



def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(f"An error occurred: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return wrapper


def get_msg_and_response_as_json(msg: str, status_code: int) -> tuple:
    """
    Get a message and a status code and return a tuple with the message and the status code
    :param msg: message to return
    :param status_code: status code to return
    :return: tuple with message and status code
    """
    return jsonify({'msg': msg}), status_code


# def process_file(file, uid: str) -> None:
#     filename = f'{uid}-{file.filename.split(".")[0]}'
#     log.info(f'filename is {file.filename}')
#     output_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.json')
#     log.info(f'Processing file {filename}')
#     pptx_processor = PptxProcessor(file=file, file_name=filename)
#     pptx_processor.save_parse_content_to_json(output_file)
#     log.info(f'File {file.filename} uploaded successfully')

@handle_error
@web_app_bp.route("/upload", methods=["POST"])
def upload_file():
    log.info('uploading file...')
    if 'file' not in request.files:
        return jsonify({'error': UNSELECTED_FILE}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': UNSELECTED_FILE}), 400
    if not file.filename.endswith(VALID_FORMATS):
        return jsonify({'error': FILE_NOT_SUPPORTED}), 400

    # if folder uploads not exist create it
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    log.info(f'generating uid for file {file.filename}')
    uid = str(uuid.uuid4())
    log.info(f'uid generated: {uid} + {file.filename.split(".")[0]}')
    filename = get_generated_filename(file.filename, uid)
    parse_pptx_to_json(file, filename)

    return jsonify({'uid': uid}), 200


@handle_error
def get_generated_filename(original_filename: str, uid: str) -> str:
    """
    Generate a unique filename for the uploaded file
    which contains the original filename, a timestamp and a uuid
    :param original_filename: original filename of the pptx file
    :param uid: unique id for the uploaded file
    :return: new filename that is unique
    :output: filename-20200101120000-uuid
    """
    original_filename = original_filename.split(".")[0]
    log.info(f'generating filename for {original_filename}')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    uploaded_filename = f'{uid}-{original_filename}-{timestamp}'
    log.info(f'uploaded filename: {uploaded_filename}')
    return uploaded_filename


# @handle_error
# @web_app_bp.route("/test", methods=["GET"])
# async def test():
#     return await explainer()

@handle_error
@web_app_bp.route("/status/<uid>", methods=["GET"])
def check_status(uid):
    log.info(f'...Checking status for file {uid}')
    # return get_status(uid)
    return get_status(uid)
