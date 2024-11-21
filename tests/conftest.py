import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Fixture para crear un cliente de prueba de FastAPI"""
    return TestClient(app)

@pytest.fixture
def valid_template_request():
    """Fixture para una solicitud válida de template"""
    return {
        "template": "minimal",
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "primaryColor": "#007bff"
    }

@pytest.fixture
def valid_webhook_config():
    """Fixture para una configuración válida de webhook"""
    return {
        "url": "http://localhost:8001/webhook",
        "secret": "test-secret",
        "description": "Test webhook"
    }
