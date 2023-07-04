# Separate system test into smaller tests, using `pytest` with `assert` statements. Use `fixture`s for running the
# web API and the Explainer. `assert` stuff like the following:
#
# - The upload method returns a UID.
# - The upload creates a file in the `uploads` folder, with the timestamp and UID in the filename.
# - The Explainer only processes new files.
# - The client raises errors when a UID is not found.
# - The status method returns a `pending` status for a file if you try right after uploading it.
# - More useful tests you can think of...

import os
from config import app
import pytest

app.config['PPTX'] = os.path.join(os.path.dirname(__file__), './sources/asyncio-intro.pptx')


class TestWeb:
    @pytest.fixture
    def client(self):
        with app.test_client() as client:
            yield client

    def test_upload(self, client):
        res = client.post('/upload', data={'file': open(app.config['PPTX'], 'rb')})
        assert res.status_code == 200
        assert os.path.exists(f'uploads/{res["uid"]}.pptx')

    def test_status(self, client):
        res = client.get('/status/36ba18ba-10e8-4f7b-b874-3ffaa3ab9145')
        assert res.status_code == 200
        assert res['status'] == 'pending'
