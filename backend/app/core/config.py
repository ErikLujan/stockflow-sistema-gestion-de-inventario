"""
Módulo de configuración principal.
Gestiona las variables de entorno y la configuración de la aplicación usando Pydantic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    Proporciona valores por defecto para desarrollo si no se establecen explícitamente.
    """
    PROJECT_NAME: str = "API de Gestión de Inventario"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de seguridad
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90
    
    # Configuración de base de datos
    DATABASE_URL: str

    # Configuración de Correos (Brevo)
    BREVO_API_KEY: str = ""
    ALERT_EMAIL_DESTINATION: str = ""

    SENDER_EMAIL: str = "eriklujan2005@gmail.com" 
    SENDER_NAME: str = "StockFlow System"
    
    # Configuración de Pydantic para cargar variables desde un archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

# Instancia única para ser importada en toda la aplicación
settings = Settings()