import asyncio
import glob
import os
from functools import wraps
from flask import jsonify
from datetime import datetime

from config import app, app_log as log, explainer_log
from models.pptx_parser import PptxProcessor
from pathlib import Path
from models.explain_generator import slides_explanations_generator


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


def parse_pptx_to_json(file, filename: str) -> None:
    log.info(f'parsing <{filename}> pptx file to json')
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'])  # Get the pptx file path

    # Process the uploaded file
    pptx_processor = PptxProcessor(file=file, file_name=filename)
    pptx_processor.save_parse_content_to_json(upload_file=uploaded_file_path)
    # start send prompt to gpt openai

    app.logger.info(f'File {filename} uploaded successfully')


def get_status(uid):
    upload_dir = app.config['UPLOAD_FOLDER']
    matching_files = [file for file in os.listdir(upload_dir) if file.startswith(uid + '_')]
    if len(matching_files) == 0:
        return jsonify({"status": "not_found"}), 404
    filename = matching_files[0]
    output_dir = app.config['OUTPUT_FOLDER']
    matching_files = [file for file in os.listdir(output_dir) if file.startswith(uid + '_')]
    if len(matching_files) == 0:
        return jsonify({
            "status": "pending",
            "filename": filename
        })

    uploaded_filename = matching_files[0].split('.')[0]
    timestamp = get_upload_timestamp(uploaded_filename)
    # todo: add explanation to the response
    return jsonify({
        "status": "done",
        "filename": uploaded_filename,
        "timestamp": timestamp,
        "explanation": []
    })


@handle_errors
async def explainer():
    explainer_log.info('Starting explainer loop')
    # Scan the uploads folder for new files from ../uploads
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*.json'))
    for file in files:
        filename = Path(file).name.split('.')[0]
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.json")

        # Check if the file has already been processed
        if not os.path.exists(output_filepath):
            explainer_log.info(f"Start generating explanations for file: {filename}")
            try:
                await slides_explanations_generator(file, filename)
                explainer_log.info(f"File processed successfully: {filename}")
            except Exception as e:
                explainer_log.error(f"Error processing file: {filename}: {e}")
            finally:
                await asyncio.sleep(3000)  # Wait for 3 mintes to avoid exceeding the API limit


def get_upload_timestamp(uploaded_file):
    explainer_log.info(f"Getting upload timestamp for file: {uploaded_file}")
    timestamp = os.path.getctime(uploaded_file)
    return datetime.fromtimestamp(timestamp).isoformat()


if __name__ == '__main__':
    # Start the explainer loop
    asyncio.run(explainer())
