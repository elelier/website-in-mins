from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from enum import Enum
import re
from jinja2 import Environment, FileSystemLoader
import time
import os
import rcssmin
import uvicorn
import traceback
import secrets
from datetime import datetime, timedelta

app = FastAPI(title="FrontPage Rapid",
             description="API para generar front pages profesionales de manera ultrarrápida")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Asegurarse de que template_name es una cadena
        if isinstance(template_name, TemplateType):
            template_name = template_name.value
            
        template = env.get_template(f"{template_name}.html")
        return template.render(**context)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al renderizar el template: {str(e)}"
        )

def minify_css(css: str) -> str:
    """Minifica el CSS usando rcssmin"""
    return rcssmin.cssmin(css)

def get_template_css(template_name: str, context: dict) -> str:
    """Lee y renderiza el CSS del template"""
    try:
        # Asegurarse de que template_name es una cadena
        if isinstance(template_name, TemplateType):
            template_name = template_name.value
            
        css_path = os.path.join(templates_dir, f"{template_name}.css")
        with open(css_path, 'r', encoding='utf-8') as f:
            css_template = f.read()
        # Renderizar el CSS con el contexto para reemplazar variables
        css = env.from_string(css_template).render(**context)
        # Minificar el CSS
        return minify_css(css)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el CSS: {str(e)}"
        )

# Almacenamiento temporal para las previsualizaciones
preview_storage = {}

class PreviewData:
    def __init__(self, html: str, css: str):
        self.html = html
        self.css = css
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=24)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

def cleanup_expired_previews():
    global preview_storage
    current_time = datetime.now()
    preview_storage = {
        token: data for token, data in preview_storage.items()
        if not data.is_expired()
    }

@app.post("/generate-frontpage", response_model=FrontPageResponse)
async def generate_frontpage(request: FrontPageRequest):
    """Genera una front page basada en el template y parámetros proporcionados"""
    start_time = time.time()
    
    try:
        # Obtener y minificar el CSS
        css = get_template_css(
            request.template,
            {
                "primary_color": request.primaryColor
            }
        )
        
        # Renderizar el HTML con el CSS minificado
        html = render_template(
            request.template,
            {
                "title": request.title,
                "subtitle": request.subtitle,
                "css": css
            }
        )
        
        # Verificar tiempo de respuesta
        generation_time = time.time() - start_time
        if generation_time > 1:
            print(f"Warning: Generation time exceeded 1 second: {generation_time:.2f}s")

        return FrontPageResponse(
            html=html,
            css=css,
            preview_url=f"/preview/{request.template}"
        )
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print("Error details:", error_details)
        raise HTTPException(status_code=500, detail=error_details)

@app.post("/generate-preview")
async def generate_preview(request: FrontPageRequest):
    # Generar el contenido
    result = await generate_frontpage(request)
    
    # Generar token único
    preview_token = secrets.token_urlsafe(16)
    
    # Almacenar los datos
    preview_storage[preview_token] = PreviewData(
        html=result.html,
        css=result.css
    )
    
    # Limpiar previsualizaciones expiradas
    cleanup_expired_previews()
    
    # Construir URL de previsualización
    preview_url = f"/preview/{preview_token}"
    
    return {"preview_url": preview_url}

@app.get("/preview/{token}")
async def get_preview(token: str):
    # Verificar si el token existe y no ha expirado
    if token not in preview_storage:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview_data = preview_storage[token]
    if preview_data.is_expired():
        del preview_storage[token]
        raise HTTPException(status_code=404, detail="Preview has expired")
    
    # Combinar HTML y CSS
    html_with_css = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>{preview_data.css}</style>
    </head>
    <body>
        {preview_data.html}
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_with_css)

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

@app.get("/", response_class=HTMLResponse)
async def test_ui():
    """Sirve la interfaz de prueba"""
    try:
        with open(os.path.join(templates_dir, "test_ui.html"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api", response_class=JSONResponse)
async def api_info():
    """Retorna información sobre la API"""
    return {
        "message": "Welcome to FrontPage Rapid API",
        "version": "1.0.0",
        "endpoints": {
            "generate-frontpage": "/generate-frontpage",
            "docs": "/docs",
            "test-ui": "/"
        }
    }

@app.get("/docs")
async def read_docs():
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
