"""
Document Processor API - Main Application
Demuestra: FastAPI, estructura de proyecto, configuración profesional.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.core.logging_config import setup_logging
from src.routes.api_routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para la aplicación."""
    # Startup
    setup_logging(settings.LOG_LEVEL, settings.LOG_FILE)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    print(f"📊 LLM Provider: {settings.LLM_PROVIDER}")
    yield
    # Shutdown
    print("👋 Aplicación cerrando...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Document Processor API

API REST para procesamiento automático de documentos con extracción inteligente de datos.

### Funcionalidades:
- 📄 **Procesamiento de archivos**: PDF, CSV, Excel, TXT, logs
- 🤖 **Extracción inteligente**: Usa LLM para extraer campos personalizados
- 📊 **Generación de reportes**: Excel, CSV, JSON
- ⚙️ **Configuración flexible**: Campos de extracción personalizables

### Caso de Negocio:
Un analista necesita procesar múltiples documentos diariamente y extraer información específica.
Esta API automatiza todo el flujo: subir archivo → procesar → extraer datos → generar reporte.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para frontend
# ADVERTENCIA: En producción, especificar dominios permitidos en lugar de "*"
# Ejemplo: allow_origins=["https://mi-dominio.com", "https://app.mi-dominio.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurar dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(api_router)


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
