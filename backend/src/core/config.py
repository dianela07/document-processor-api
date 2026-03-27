"""
Configuración centralizada de la aplicación.
Demuestra: Variables de entorno, buenas prácticas, configuración limpia.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno."""
    
    # Información de la aplicación
    APP_NAME: str = "Document Processor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Base de datos SQLite
    DATABASE_URL: str = "sqlite:///data/document_processor.db"
    
    # LLM Provider: "groq", "ollama", "azure", "none"
    LLM_PROVIDER: str = "groq"
    
    # Groq (Gratuito - Recomendado)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    # Ollama (Local - 100% Gratuito)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Azure OpenAI (De pago)
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Configuración de procesamiento
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_FORMATS: list[str] = [".pdf", ".csv", ".xlsx", ".xls", ".txt", ".log"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Singleton para obtener la configuración."""
    return Settings()


# Instancia global
settings = get_settings()
