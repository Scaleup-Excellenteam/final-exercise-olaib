import os
import sys
import json
import time
import argparse
from functools import wraps

from status import Status, PythonClient
from config import LOGS_DIR, EXPLANATIONS_DIR, client_log, INTERVAL_BETWEEN_STATUS_CHECKS


def parse_arguments():
    parser = argparse.ArgumentParser(description="Slide Explanation Generator")
    parser.add_argument("file", type=argparse.FileType("r"),
                        help="Path to the pptx file including the .pptx at the end")
    return parser.parse_args()


def handle_exceptions(func):
    """ Decorator that handles exceptions in a function and logs them.
    :param func: the function to decorate.
    :return: a decorator that handles exceptions in a function and logs them.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """ Handles exceptions in a function and logs them.
        :param args: the arguments of the function.
        :param kwargs: the keyword arguments of the function.
        :return: the function's return value.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            sys.exit(1)

    return wrapper


def print_status_into_log(status: Status) -> None:
    """ Prints the status of the file that was uploaded and processed successfully
    into the client log file
    :param status: the status of the file that was uploaded and processed successfully
    """
    for key, value in status.__dict__.items():
        client_log.info(f"{key.capitalize()}: {value}")


def check_log_dir():
    log_dir = os.path.dirname(os.path.abspath(__file__)) + '/' + LOGS_DIR
    check_and_create_dir(log_dir)


def check_and_create_dir(dir_path: str) -> None:
    """Checks if the directory exists and creates it if it doesn't
    :param dir_path: the path of the directory to check
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def create_explanation_file(status: Status) -> None:
    f"""Creates a file for the explanation of the file that was uploaded and processed successfully
    into the explanations directory with the name of the file and the timestamp of the upload time
    :param status: the status of the file that was uploaded and processed successfully
    for example: "{EXPLANATIONS_DIR}/file_name_2021-01-01_12-00-00.json"
    """
    file_name = status.filename + "_" + status.timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    path = f"{EXPLANATIONS_DIR}/{file_name}.json"
    explanation = status.explanation

    check_and_create_dir(EXPLANATIONS_DIR)
    print("Creating explanation file...")
    with open(path, "w") as explanation_file:
        json.dump(explanation, explanation_file)
    print(f"Explanation file created successfully in the path: {path}")


@handle_exceptions
def main():
    args = parse_arguments()
    check_log_dir()
    print(f"Please check the {LOGS_DIR} directory for more information about the process")
    client = PythonClient()
    file_path = args.file.name
    client_log.info(f"file path: {file_path}")
    try:
        uid = client.upload(file_path)
        client_log.info(f"got uid: {uid}")
        print("File uploaded successfully")
        while True:
            status = client.status(uid)
            print("Waiting for file to be processed...")
            print_status_into_log(status)
            if status.is_done():
                create_explanation_file(status)
                break
            else:
                time.sleep(INTERVAL_BETWEEN_STATUS_CHECKS)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
