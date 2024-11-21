from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the templates directory as a static files directory
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class TemplateSelect(BaseModel):
    template: str

class WebsiteGeneration(BaseModel):
    template: str
    title: str
    subtitle: str
    primaryColor: str

VALID_TEMPLATES = ['minimal', 'corporate', 'creative']

@app.get("/")
async def template_selection():
    return FileResponse("templates/preview.html")

@app.get("/{template_name}.html")
async def get_template(template_name: str):
    if template_name not in VALID_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(f"templates/{template_name}.html")

@app.post("/api/select-template")
async def select_template(template_data: TemplateSelect):
    if template_data.template not in VALID_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid template name. Must be one of: {', '.join(VALID_TEMPLATES)}"
        )
    
    return {
        "success": True,
        "template": template_data.template,
        "message": f"Successfully selected {template_data.template} template"
    }

@app.get("/editor")
async def editor():
    return FileResponse("templates/test_ui.html")

@app.post("/api/generate-frontpage")
async def generate_frontpage(data: WebsiteGeneration):
    if data.template not in VALID_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail={"error": f"Invalid template name. Must be one of: {', '.join(VALID_TEMPLATES)}"}
        )
    
    try:
        # Read the template file
        template_path = f"templates/{data.template}.html"
        css_path = f"templates/{data.template}.css"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Replace placeholders in the template
        html_content = html_content.replace("{{title}}", data.title)
        html_content = html_content.replace("{{subtitle}}", data.subtitle)
        css_content = css_content.replace("{{primaryColor}}", data.primaryColor)
        
        return JSONResponse({
            "html": html_content,
            "css": css_content
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Error generating website: {str(e)}"}
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
