import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_frontpage_with_html_css_export():
    """Test that the /generate-frontpage endpoint returns valid HTML and minified CSS"""
    request_data = {
        "template": "minimal",
        "title": "Test Website",
        "subtitle": "Testing HTML and CSS Export",
        "primaryColor": "#4A90E2"
    }
    
    response = client.post("/generate-frontpage", json=request_data)
    
    # Print response details for debugging
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Content: {response.content.decode()}")
    
    # Verificar que la respuesta es exitosa
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # Verificar que la respuesta contiene HTML y CSS
    data = response.json()
    assert "html" in data, "Response does not contain HTML"
    assert "css" in data, "Response does not contain CSS"
    
    # Verificar que el HTML es válido y contiene los elementos esperados
    html = data["html"]
    assert "<!DOCTYPE html>" in html, "HTML does not contain DOCTYPE declaration"
    assert "<html lang=\"es\">" in html, "HTML does not contain lang attribute"
    assert request_data["title"] in html, f"HTML does not contain title '{request_data['title']}'"
    assert request_data["subtitle"] in html, f"HTML does not contain subtitle '{request_data['subtitle']}'"
    
    # Verificar que el CSS está minificado
    css = data["css"]
    assert css, "CSS is empty"
    assert len(css.split("\n")) == 1, "CSS is not minified"
    assert "#4A90E2" in css, "CSS does not contain primary color"
    
    # Verificar que no hay espacios innecesarios en el CSS minificado
    assert "  " not in css, "CSS contains unnecessary spaces"
    
    print("Test successful! HTML and CSS export is working correctly.")
    print("\nGenerated HTML preview:")
    print("------------------------")
    print(html[:500] + "..." if len(html) > 500 else html)
    print("\nGenerated CSS preview:")
    print("----------------------")
    print(css[:500] + "..." if len(css) > 500 else css)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
