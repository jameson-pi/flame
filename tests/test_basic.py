import pytest
from flame.api.client import APIClient

def test_client_init():
    # This will fail without an API key, so we mock or handle it
    import os
    os.environ["FLAME_API_KEY"] = "fake-key"
    client = APIClient()
    assert client.api_key == "fake-key"
