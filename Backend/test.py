import os
import pytest
from .config import app


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
