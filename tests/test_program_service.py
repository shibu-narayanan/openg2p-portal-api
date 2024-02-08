from fastapi.testclient import TestClient
from openg2p_fastapi_common.context import app_registry

# from .config import Settings
# _config = Settings.get_config()
from .base_setup import base_setup

base_setup()

client = TestClient(app_registry.get())


def test_read_main():
    response = client.get("/programsummary")

    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
