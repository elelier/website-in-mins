import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_templates():
    """Verifica que se listen los 3 templates disponibles"""
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que hay exactamente 3 templates
    assert "templates" in data
    assert len(data["templates"]) == 3
    
    # Verificar que están todos los templates requeridos
    template_ids = [t["id"] for t in data["templates"]]
    assert "minimal" in template_ids
    assert "corporate" in template_ids
    assert "creative" in template_ids

def test_preview_templates():
    """Verifica que funcione la vista previa de cada template"""
    templates = ["minimal", "corporate", "creative"]
    
    for template in templates:
        response = client.get(f"/preview/{template}")
        assert response.status_code == 200
        
        # Verificar que el contenido es HTML
        assert "<!DOCTYPE html>" in response.text
        assert "<html" in response.text
        assert "</html>" in response.text
        
        # Verificar que contiene los elementos de ejemplo
        assert "Ejemplo de Título" in response.text
        assert "Este es un subtítulo de ejemplo" in response.text

def test_generate_with_different_templates():
    """Verifica la generación de páginas con diferentes templates"""
    test_data = {
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "primaryColor": "#FF0000"
    }
    
    for template in ["minimal", "corporate", "creative"]:
        response = client.post(
            "/generate-frontpage",
            json={**test_data, "template": template}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "html" in data
        assert "css" in data
        assert "preview_url" in data
        
        # Verificar que el HTML contiene los datos proporcionados
        assert test_data["title"] in data["html"]
        assert test_data["subtitle"] in data["html"]
        assert test_data["primaryColor"] in data["html"]

def test_invalid_template():
    """Verifica que se maneje correctamente un template inválido"""
    response = client.post(
        "/generate-frontpage",
        json={
            "template": "invalid_template",
            "title": "Test Title",
            "subtitle": "Test Subtitle",
            "primaryColor": "#FF0000"
        }
    )
    
    assert response.status_code == 422  # Validation Error

def test_template_preview_invalid():
    """Verifica que se maneje correctamente una solicitud de preview inválida"""
    response = client.get("/preview/invalid_template")
    assert response.status_code == 422  # Validation Error

if __name__ == "__main__":
    pytest.main(["-v", __file__])
