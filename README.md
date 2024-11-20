# FrontPage Rapid

API para generar front pages profesionales de manera ultrarrápida con personalización mínima.

## Características

- Generación de página web con un solo endpoint
- Personalización básica (título, subtítulo, color principal)
- 3 templates predefinidos (minimal, corporate, creative)
- Exportación a HTML/CSS estático
- Tiempo de generación < 1 segundo

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Iniciar el servidor:
```bash
uvicorn main:app --reload
```

### Endpoint Principal

```bash
POST /generate-frontpage
```

Ejemplo de request:
```json
{
  "template": "minimal",
  "title": "Mi Página Web",
  "subtitle": "Bienvenidos a mi sitio",
  "primaryColor": "#007bff"
}
```

Respuesta:
```json
{
  "html": "string",
  "css": "string",
  "preview_url": "string"
}
```

## Stack Tecnológico

- Backend: Python (FastAPI)
- Generación de Templates: Jinja2
- Documentación API: Swagger UI (automático via FastAPI)

## Documentación

Una vez iniciado el servidor, puedes acceder a la documentación interactiva en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
