from functools import wraps

from requests import Response
import requests
from datetime import datetime
from dataclasses import dataclass
from config import DONE, UPLOAD_URL, GET_STATUS_URL, UID_PARAM, STATUS_PARAM, FILENAME_PARAM,\
    TIMESTAMP_PARAM,EXPLANATION_PARAM

@dataclass
class Status:
    """ A class representing the status of a file that was uploaded to the server

    Attributes:
        status (str): the status of the file
        filename (str): the name of the file
        timestamp (datetime): the time the file was uploaded
        explanation (str): an explanation of the status
    """
    status: str
    filename: str
    timestamp: datetime
    explanation: str

    def is_done(self):
        print(f"Got status: {self.status}")
        return self.status == DONE

    def to_str(self):
        """ Returns to string representation of the status as json format
        :return: the string representation of the status
        """
        attributes = vars(self)
        return "\n".join(f"{key.capitalize()}: {value}" for key, value in attributes.items())


def check_status_code(func: callable) -> callable:
    """ A decorator that checks the status code of the response and raises an exception if it is not 200
    :param func: the function to decorate
    :return: the decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response.raise_for_status()
        return response

    return wrapper


class PythonClient:
    """ A class representing a python client that can upload files to the server and get their status
    """

    def __init__(self):
        self.session = requests.Session()

    @check_status_code
    def _send_request(self, url: str, method: str = "GET", **kwargs) -> Response:
        """ Sends a request to the server and returns the response
        :param url: the url of the request
        :param method: the method of the request
        :param kwargs: the arguments of the request
        :return: the response of the request
        """
        return self.session.request(method, url, **kwargs)

    def upload(self, file_path: str) -> str:
        """ Uploads a file to the server and returns the uid of the file
        :param file_path: the path of the file to upload
        :return: the uid of the file
        """
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = self._send_request(UPLOAD_URL, method="POST", files=files)
            return response.json()[UID_PARAM]

    def status(self, uid: str) -> Status:
        response = self._send_request(f"{GET_STATUS_URL}/{uid}")
        response_json = response.json()
        return Status(
            status=response_json[STATUS_PARAM],
            filename=response_json[FILENAME_PARAM],
            timestamp=datetime.fromisoformat(response_json[TIMESTAMP_PARAM]),
            explanation=response_json[EXPLANATION_PARAM]
        )
