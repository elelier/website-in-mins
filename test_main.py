import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

def test_generate_frontpage_success():
    """Test successful page generation with valid inputs"""
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "primaryColor": "#007bff"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "html" in data
    assert "css" in data
    assert "preview_url" in data
    
    # Verificar contenido HTML
    assert "Test Title" in data["html"]
    assert "Test Subtitle" in data["html"]
    assert "#007bff" in data["html"]

def test_response_time():
    """Test that response time is under 1 second"""
    start_time = time.time()
    
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "Performance Test",
            "subtitle": "Testing Response Time",
            "primaryColor": "#ff0000"
        }
    )
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    assert generation_time < 1.0
    assert response.status_code == 200

def test_input_validation():
    """Test input validation for all fields"""
    # Test título vacío
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "",
            "subtitle": "Test Subtitle",
            "primaryColor": "#007bff"
        }
    )
    assert response.status_code == 422

    # Test subtítulo muy largo (>200 caracteres)
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "Test Title",
            "subtitle": "x" * 201,
            "primaryColor": "#007bff"
        }
    )
    assert response.status_code == 422

    # Test color inválido
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "primaryColor": "invalid-color"
        }
    )
    assert response.status_code == 422

    # Test template inválido
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "invalid-template",
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "primaryColor": "#007bff"
        }
    )
    assert response.status_code == 422

def test_template_rendering():
    """Test that template is properly rendered with custom values"""
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "minimal",
            "title": "Custom Title",
            "subtitle": "Custom Subtitle",
            "primaryColor": "#ff5733"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que los valores personalizados están en el HTML
    assert "Custom Title" in data["html"]
    assert "Custom Subtitle" in data["html"]
    assert "#ff5733" in data["html"]
    
    # Verificar estructura HTML básica
    assert "<!DOCTYPE html>" in data["html"]
    assert "<html" in data["html"]
    assert "</html>" in data["html"]

if __name__ == "__main__":
    pytest.main(["-v", __file__])