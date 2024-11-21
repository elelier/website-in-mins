from enum import Enum
from typing import Optional
from pydantic import BaseModel, field_validator, HttpUrl
import re

class TemplateType(str, Enum):
    minimal = "minimal"
    corporate = "corporate"
    creative = "creative"
    portfolio = "portfolio"
    landing = "landing"
    blog = "blog"

class FontFamily(str, Enum):
    roboto = "Roboto, sans-serif"
    open_sans = "Open Sans, sans-serif"
    lato = "Lato, sans-serif"
    montserrat = "Montserrat, sans-serif"
    poppins = "Poppins, sans-serif"

class ImagePosition(str, Enum):
    left = "left"
    right = "right"
    center = "center"
    background = "background"

class FrontPageRequest(BaseModel):
    template: TemplateType = TemplateType.minimal
    title: str
    subtitle: str
    primaryColor: str
    secondaryColor: str = "#ffffff"
    fontFamily: FontFamily = FontFamily.roboto
    heroImage: Optional[HttpUrl] = None
    imagePosition: Optional[ImagePosition] = None
    customCss: Optional[str] = None
    metaDescription: Optional[str] = None

    @field_validator('title')
    def validate_title(cls, v):
        if len(v) > 100:
            raise ValueError('Title must be less than 100 characters')
        return v

    @field_validator('subtitle')
    def validate_subtitle(cls, v):
        if len(v) > 200:
            raise ValueError('Subtitle must be less than 200 characters')
        return v

    @field_validator('primaryColor', 'secondaryColor')
    def validate_color(cls, v):
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', v):
            raise ValueError('Invalid hex color code')
        return v

    @field_validator('customCss')
    def validate_css(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Custom CSS must be less than 1000 characters')
        return v

class FrontPageResponse(BaseModel):
    html: str
    css: str
    preview_url: str

class WebhookConfig(BaseModel):
    url: HttpUrl
    secret: Optional[str] = None
    description: Optional[str] = None
    active: bool = True

class GenerationEvent(BaseModel):
    event_id: str
    template_type: str
    timestamp: str
    status: str
    details: dict
