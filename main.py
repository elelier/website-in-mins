from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator
from enum import Enum
import re
from jinja2 import Environment, FileSystemLoader
import time
import os

app = FastAPI(title="FrontPage Rapid",
             description="API para generar front pages profesionales de manera ultrarrápida")

# Configuración de Jinja2
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

# Modelo de datos para la validación de entrada
class TemplateType(str, Enum):
    minimal = "minimal"
    corporate = "corporate"
    creative = "creative"

class FrontPageRequest(BaseModel):
    template: TemplateType = "minimal"
    title: str
    subtitle: str
    primaryColor: str

    @field_validator("title")
    def validate_title(cls, v):
        if not v or len(v) > 100:
            raise ValueError("El título debe tener entre 1 y 100 caracteres")
        return v

    @field_validator("subtitle")
    def validate_subtitle(cls, v):
        if not v or len(v) > 200:
            raise ValueError("El subtítulo debe tener entre 1 y 200 caracteres")
        return v

    @field_validator("primaryColor")
    def validate_color(cls, v):
        if not re.match("^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("El color debe estar en formato hexadecimal (#RRGGBB)")
        return v

class FrontPageResponse(BaseModel):
    html: str
    css: str
    preview_url: str

def render_template(template_name: str, context: dict) -> str:
    """Renderiza un template con el contexto proporcionado"""
    try:
        template = env.get_template(f"{template_name}.html")
        return template.render(**context)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al renderizar el template: {str(e)}"
        )

@app.post("/generate-frontpage", response_model=FrontPageResponse)
async def generate_frontpage(request: FrontPageRequest):
    """Genera una front page basada en el template y parámetros proporcionados"""
    start_time = time.time()
    
    try:
        # Renderizar el template seleccionado
        html = render_template(
            request.template,
            {
                "title": request.title,
                "subtitle": request.subtitle,
                "primary_color": request.primaryColor
            }
        )
        
        # Verificar tiempo de respuesta
        generation_time = time.time() - start_time
        if generation_time > 1:
            print(f"Warning: Generation time exceeded 1 second: {generation_time:.2f}s")

        return FrontPageResponse(
            html=html,
            css="",  # CSS está embebido en el HTML
            preview_url=f"/preview/{request.template}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preview/{template_type}", response_class=HTMLResponse)
async def preview_template(template_type: TemplateType):
    """Muestra una vista previa del template seleccionado con datos de ejemplo"""
    try:
        preview_data = {
            "title": "Ejemplo de Título",
            "subtitle": "Este es un subtítulo de ejemplo para mostrar cómo se ve el template",
            "primary_color": "#4A90E2"
        }
        
        html = render_template(template_type, preview_data)
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar la vista previa: {str(e)}"
        )

@app.get("/templates", response_model=dict)
async def list_templates():
    """Lista todos los templates disponibles con sus descripciones"""
    return {
        "templates": [
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Diseño minimalista y elegante",
                "preview_url": "/preview/minimal"
            },
            {
                "id": "corporate",
                "name": "Corporate",
                "description": "Diseño profesional para empresas",
                "preview_url": "/preview/corporate"
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Diseño creativo con animaciones",
                "preview_url": "/preview/creative"
            }
        ]
    }

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to FrontPage Rapid API",
        "version": "1.0.0",
        "endpoints": {
            "generate-frontpage": "/generate-frontpage",
            "preview": "/preview/{template_type}",
            "templates": "/templates",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
