from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Información de la aplicación
    APP_NAME: str = "FrontPage Rapid"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = """
    🚀 API para generar front pages profesionales de manera ultrarrápida.
    
    ## 🎯 Características Principales
    * Templates Profesionales (6 diseños predefinidos)
    * Personalización Completa
    * Optimización y Rendimiento
    * Sistema de Caché
    * Webhooks en tiempo real
    
    Visita /docs para la documentación completa.
    """
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Configuración de caché
    CACHE_TTL: int = 3600  # 1 hora en segundos
    PREVIEW_EXPIRY_HOURS: int = 24

    # Configuración de seguridad
    MAX_CSS_LENGTH: int = 10000  # Máximo número de caracteres en el CSS personalizado

    class Config:
        env_file = ".env"

settings = Settings()
