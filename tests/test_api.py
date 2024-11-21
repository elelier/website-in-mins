import pytest
import time
from datetime import datetime, timedelta
from app.services.renderer import PreviewData

def test_generate_frontpage_success(client, valid_template_request):
    """Test successful page generation with valid inputs"""
    response = client.post("/api/generate-frontpage", json=valid_template_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "html" in data
    assert "css" in data
    assert "preview_url" in data
    assert valid_template_request["title"] in data["html"]
    assert valid_template_request["subtitle"] in data["html"]
    assert valid_template_request["primaryColor"] in data["css"]

def test_response_time(client, valid_template_request):
    """Test that response time is under 1 second"""
    start_time = time.time()
    response = client.post("/api/generate-frontpage", json=valid_template_request)
    generation_time = time.time() - start_time
    
    assert generation_time < 1.0
    assert response.status_code == 200

def test_input_validation(client):
    """Test input validation for all fields"""
    invalid_requests = [
        # Template inválido
        {
            "template": "invalid_template",
            "title": "Test",
            "subtitle": "Test",
            "primaryColor": "#000000"
        },
        # Color inválido
        {
            "template": "minimal",
            "title": "Test",
            "subtitle": "Test",
            "primaryColor": "not-a-color"
        },
        # Título muy largo
        {
            "template": "minimal",
            "title": "T" * 101,
            "subtitle": "Test",
            "primaryColor": "#000000"
        }
    ]
    
    for req in invalid_requests:
        response = client.post("/api/generate-frontpage", json=req)
        assert response.status_code == 422

def test_preview_functionality(client, valid_template_request):
    """Test preview generation and access"""
    # Generar preview
    response = client.post("/api/generate-preview", json=valid_template_request)
    assert response.status_code == 200
    data = response.json()
    assert "preview_url" in data
    
    # Acceder al preview
    preview_token = data["preview_url"].split("/")[-1]
    response = client.get(f"/api/preview/{preview_token}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    # Token inválido
    response = client.get("/api/preview/invalid-token")
    assert response.status_code == 404

def test_template_list(client):
    """Test template listing endpoint"""
    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    
    expected_templates = ["minimal", "corporate", "creative", "portfolio", "landing", "blog"]
    templates = [t["id"] for t in data]
    
    assert all(t in templates for t in expected_templates)
    assert all("description" in t for t in data)

def test_api_info(client):
    """Test API information endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    
    assert "version" in data
    assert "templates" in data
    assert "features" in data
