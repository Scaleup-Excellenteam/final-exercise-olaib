import os
from functools import wraps
from flask import jsonify, request
from datetime import datetime
from config import app, logger as log
from models.pptx_parser import PptxProcessor

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            slide_number = args[0]
            app.logger.error(f"An error occurred for slide {slide_number}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return wrapper


def generate_explanation_from_openai(file):
    pass


def parse_pptx_to_json(file, filename: str) -> None:
    log.info(f'parsing <{filename}> pptx file to json')
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'])  # Get the pptx file path

    # Process the uploaded file
    pptx_processor = PptxProcessor(file=file, file_name=filename)
    pptx_processor.save_parse_content_to_json(upload_file=uploaded_file_path)

    app.logger.info(f'File {filename} uploaded successfully')


def get_status(uid):
    upload_dir = app.config['UPLOAD_FOLDER']
    # //find file that start with uid
    matching_files = [file for file in os.listdir(upload_dir) if file.startswith(uid)]
    if len(matching_files) == 0:
        return jsonify({"status": "not_found"}), 404

    output_dir = app.config['OUTPUT_FOLDER']
    matching_files = [file for file in os.listdir(output_dir) if file.startswith(uid)]
    uploaded_filename, timestamp = '', ''
    if len(matching_files) == 0:
        timestamp = get_upload_timestamp(uploaded_filename)
        uploaded_filename = matching_files[0].split('.')[0]
        return jsonify({
            "status": "pending",
            "filename": uploaded_filename,
            "timestamp": timestamp,
            "explanation": None
        })

    # get the prompts from the file
    # send to openai
    # get the explanation
    # return the explanation
    # explanation = PptxProcessor.
    #
    # return jsonify({
    #     "status": "done",
    #     "filename": filename,
    #     "timestamp": get_upload_timestamp(uploaded_file),
    #     "explanation": explanation
    # })


def get_upload_timestamp(uploaded_file):
    timestamp = os.path.getctime(uploaded_file)
    return datetime.fromtimestamp(timestamp).isoformat()

