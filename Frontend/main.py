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
        res = func(*args, **kwargs)
        if res.status_code == 200:
            try:
                return res.json()
            except ValueError:
                raise Exception(f"Error: Invalid JSON response - {res.text}")
        else:
            raise Exception(f"Error: {res.status_code} - {res.text}")

    return wrapper


@check_status_code
def upload_file_to_server(file_path: str) -> Response:
    files = {"file": open(file_path, "rb")}
    response = requests.post(UPLOAD_URL, files=files)
    return response


def main():
    try:
        res = upload_file_to_server(FILE_PATH)
        print(res)
        # get_status_response = requests.get(f"{GET_STATUS_URL}/{res['uid']}")
        # print(get_status_response.json())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
