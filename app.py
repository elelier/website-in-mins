from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel

app = FastAPI()

# Mount the templates directory as a static files directory
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

class TemplateSelect(BaseModel):
    template: str

VALID_TEMPLATES = ['minimal', 'corporate', 'creative']

@app.get("/")
async def template_selection():
    return FileResponse("templates/preview.html")

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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
