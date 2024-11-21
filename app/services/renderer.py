from jinja2 import Environment, FileSystemLoader
import rcssmin
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
from collections import OrderedDict

from app.core.config import settings

# Caché en memoria con límite de tamaño
class MemoryCache:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.expiry = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self.cache:
            return None
        
        if key in self.expiry and datetime.now() > self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
            return None
            
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: str, ttl: int = None):
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
            
        self.cache[key] = value
        self.cache.move_to_end(key)
        
        if ttl:
            self.expiry[key] = datetime.now() + timedelta(seconds=ttl)

# Instancia global del caché
cache = MemoryCache()

# Configuración de Jinja2
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(templates_dir)))

class PreviewData:
    def __init__(self, html: str, css: str):
        self.html = html
        self.css = css
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=settings.PREVIEW_EXPIRY_HOURS)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

def get_cache_key(template_name: str, context: dict) -> str:
    context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()
    return f"template:{template_name}:{context_hash}"

def get_template(template_name: str):
    return env.get_template(f"{template_name}.html")

def get_cached_render(template_name: str, context: dict) -> Optional[Dict[str, str]]:
    cache_key = get_cache_key(template_name, context)
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    rendered = render_template(template_name, context)
    if rendered:
        cache.set(
            cache_key,
            json.dumps(rendered),
            ttl=settings.CACHE_TTL
        )
    return rendered

def render_template(template_name: str, context: dict) -> Dict[str, str]:
    template = get_template(template_name)
    css = get_template_css(template_name, context)
    context["css"] = minify_css(css)
    html = template.render(**context)
    return {"html": html, "css": css}

def minify_css(css: str) -> str:
    return rcssmin.cssmin(css)

def get_template_css(template_name: str, context: dict) -> str:
    css_template = env.get_template(f"{template_name}_style.html")
    return css_template.render(**context)
