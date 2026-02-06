from fastapi.testclient import TestClient
import sys
sys.path.append("..")
from main import app

client = TestClient(app)

def test_app_running():
    response = client.get("/")
    assert response.status_code in [200, 404]