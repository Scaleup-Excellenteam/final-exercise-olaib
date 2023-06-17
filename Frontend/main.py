from functools import wraps
from requests import Response
import requests

URL = "http://localhost:5000"
UPLOAD_URL = f"{URL}/upload"
GET_STATUS_URL = f"{URL}/status"
FILE_PATH = "sources/asyncio-intro.pptx"


def check_status_code(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                raise Exception(f"Error: Invalid JSON response - {response.text}")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    return wrapper


@check_status_code
def upload_file_to_server(file_path: str) -> Response:
    files = {"file": open(file_path, "rb")}
    response = requests.post(UPLOAD_URL, files=files)
    return response

@check_status_code
def get_status(uid: str) -> Response:
    response = requests.get(f"{GET_STATUS_URL}/{uid}")
    return response


def main():
    try:
        # res = upload_file_to_server(FILE_PATH)
        # print(res)
        # uid = res["uid"]
        uid = '36ba18ba-10e8-4f7b-b874-3ffaa3ab9145'
        print(f"UID: {uid}")
        res = get_status(uid)
        print(res)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
