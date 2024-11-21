from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
import secrets
from datetime import datetime
from typing import Dict

from app.models.schemas import (
    FrontPageRequest,
    FrontPageResponse,
    WebhookConfig,
    GenerationEvent,
    TemplateType,
    FontFamily
)
from app.services.renderer import get_cached_render, PreviewData
from app.services.webhooks import webhooks, notify_generation_event
from app.core.config import settings
from app.core.error_handling import NotFoundError, ValidationError, ServerError
from app.core.json_rate_limiter import rate_limiter_dependency
from fastapi.security import OAuth2PasswordBearer
from app.core.auth import decode_access_token

router = APIRouter()

# Almacenamiento temporal para las previsualizaciones
preview_storage: Dict[str, PreviewData] = {}

def cleanup_expired_previews():
    """Limpia las previsualizaciones expiradas"""
    expired = [token for token, data in preview_storage.items() if data.is_expired()]
    for token in expired:
        del preview_storage[token]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return payload

@router.get("/", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
def root():
    """Página principal"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FrontPage Rapid API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            a { color: #0066cc; text-decoration: none; margin-right: 20px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>FrontPage Rapid API</h1>
        <p>Bienvenido a la API de generación de páginas web.</p>
        <div>
            <a href="/test">Interfaz de Prueba</a>
            <a href="/docs">Documentación (Swagger)</a>
            <a href="/redoc">Documentación (ReDoc)</a>
        </div>
    </body>
    </html>
    """)

@router.post("/generate-frontpage", response_model=FrontPageResponse, dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def generate_frontpage(request: FrontPageRequest):
    """Genera una front page basada en el template y parámetros proporcionados"""
    try:
        rendered = get_cached_render(request.template.value, request.model_dump())
        if not rendered:
            raise ServerError()
        
        # Generar token único para previsualización
        token = secrets.token_urlsafe(16)
        preview_storage[token] = PreviewData(**rendered)
        preview_url = f"/preview/{token}"
        
        # Notificar evento
        event = GenerationEvent(
            event_id=token,
            template_type=request.template.value,
            timestamp=datetime.now().isoformat(),
            status="success",
            details=request.model_dump()
        )
        await notify_generation_event(event)
        
        return FrontPageResponse(
            html=rendered["html"],
            css=rendered["css"],
            preview_url=preview_url
        )
    except ValidationError as e:
        raise HTTPException(status_code=e.code, detail=str(e))
    except ServerError as e:
        raise HTTPException(status_code=e.code, detail=str(e))

@router.post("/generate-preview", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def generate_preview(request: FrontPageRequest):
    """Genera una previsualización temporal"""
    try:
        rendered = get_cached_render(request.template.value, request.model_dump())
        if not rendered:
            raise ServerError()
        
        token = secrets.token_urlsafe(16)
        preview_storage[token] = PreviewData(**rendered)
        
        return {"preview_url": f"/preview/{token}"}
    except ValidationError as e:
        raise HTTPException(status_code=e.code, detail=str(e))
    except ServerError as e:
        raise HTTPException(status_code=e.code, detail=str(e))

@router.get("/preview/{token}", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def get_preview(token: str):
    """Obtiene una previsualización por su token"""
    cleanup_expired_previews()
    
    if token not in preview_storage:
        raise NotFoundError()
    
    preview = preview_storage[token]
    if preview.is_expired():
        del preview_storage[token]
        raise NotFoundError()
    
    return HTMLResponse(
        f"<style>{preview.css}</style>{preview.html}"
    )

@router.get("/templates", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def list_templates():
    """Lista todos los templates disponibles con sus descripciones"""
    templates = [
        {
            "id": t.value,
            "name": t.name.title(),
            "description": "Template profesional para " + t.name
        }
        for t in TemplateType
    ]
    return templates

@router.get("/info", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def api_info():
    """Retorna información sobre la API"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "templates": [t.value for t in TemplateType],
        "features": {
            "template_customization": True,
            "preview_generation": True,
            "webhook_notifications": True,
            "css_minification": True,
            "caching": True,
            "responsive_design": True
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "generate": "/generate-frontpage",
            "preview": "/generate-preview",
            "templates": "/templates",
            "webhooks": "/webhooks"
        },
        "fonts_available": [
            "Roboto, sans-serif",
            "Open Sans, sans-serif",
            "Lato, sans-serif",
            "Montserrat, sans-serif",
            "Poppins, sans-serif"
        ]
    }

# Endpoints de Webhooks
@router.post("/webhooks", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def register_webhook(webhook: WebhookConfig):
    """Registra un nuevo webhook"""
    webhook_id = secrets.token_urlsafe(16)
    webhooks[webhook_id] = webhook
    return {"id": webhook_id, **webhook.model_dump()}

@router.get("/webhooks", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def list_webhooks():
    """Lista todos los webhooks registrados"""
    return [{"id": id, **webhook.model_dump()} for id, webhook in webhooks.items()]

@router.put("/webhooks/{webhook_id}", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def update_webhook(webhook_id: str, webhook: WebhookConfig):
    """Actualiza un webhook existente"""
    if webhook_id not in webhooks:
        raise NotFoundError()
    webhooks[webhook_id] = webhook
    return {"id": webhook_id, **webhook.model_dump()}

@router.delete("/webhooks/{webhook_id}", dependencies=[Depends(rate_limiter_dependency), Depends(get_current_user)])
async def delete_webhook(webhook_id: str):
    """Elimina un webhook"""
    if webhook_id not in webhooks:
        raise NotFoundError()
    del webhooks[webhook_id]
    return {"message": "Webhook deleted"}
