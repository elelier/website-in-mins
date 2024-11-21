import pytest
from app.services.renderer import (
    render_template,
    get_template_css,
    minify_css,
    get_cached_render,
    cache
)

def setup_function():
    """Limpiar el caché antes de cada test"""
    cache.cache.clear()
    cache.expiry.clear()

def test_template_loading():
    """Test template loading"""
    context = {
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "primaryColor": "#007bff"
    }
    html = render_template("minimal", context)
    assert html is not None
    assert isinstance(html, dict)
    assert "html" in html
    assert "css" in html

def test_template_rendering():
    """Test template rendering with context"""
    context = {
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "primaryColor": "#007bff",
        "secondaryColor": "#ffffff",
        "fontFamily": "Roboto, sans-serif"
    }
    html = render_template("minimal", context)
    assert context["title"] in html["html"]
    assert context["subtitle"] in html["html"]
    assert context["primaryColor"] in html["css"]

def test_css_generation():
    """Test CSS generation and minification"""
    context = {
        "primaryColor": "#007bff",
        "secondaryColor": "#ffffff",
        "fontFamily": "Roboto, sans-serif"
    }
    css = get_template_css("minimal", context)
    assert css is not None
    assert context["primaryColor"] in css
    assert context["secondaryColor"] in css
    assert context["fontFamily"] in css

def test_caching():
    """Test template caching functionality"""
    context = {
        "title": "Cache Test",
        "subtitle": "Testing Cache",
        "primaryColor": "#ff0000"
    }

    # Primera renderización (debería guardar en caché)
    first_render = get_cached_render("minimal", context)
    assert first_render is not None

    # Segunda renderización (debería usar caché)
    second_render = get_cached_render("minimal", context)
    assert second_render is not None
    assert first_render == second_render

def test_template_variations():
    """Test different template types"""
    templates = ["minimal"]  # Por ahora solo probamos minimal
    context = {
        "title": "Test",
        "subtitle": "Test",
        "primaryColor": "#000000",
        "secondaryColor": "#ffffff",
        "fontFamily": "Roboto, sans-serif"
    }

    for template_name in templates:
        html = render_template(template_name, context)
        assert html is not None
        assert isinstance(html, dict)
        assert "html" in html
        assert "css" in html
