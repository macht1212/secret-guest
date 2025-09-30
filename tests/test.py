import pytest
import os

os.environ['APP_ENV'] = 'testing'

@pytest.fixture
def test_client():
    from app.src.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)
