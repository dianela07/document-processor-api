"""
Rutas de la API REST - FastAPI
Demuestra: Framework web, endpoints RESTful, manejo de archivos.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime
import io
import logging

from src.processor.processor import DocumentProcessor, ProcessorSettings
from src.database.db import ProcessesDB, FieldsDB
from src.reports.generator import ReportGenerator
from src.models.schemas import ExtractionField, APIResponse, ReportConfig
from src.llm.providers import get_llm_provider
from src.core.config import settings

logger = logging.getLogger(__name__)

# Inicialización de componentes
router = APIRouter(prefix="/api/v1", tags=["Document Processing"])
process_settings = ProcessorSettings()
db = ProcessesDB()
fields_db = FieldsDB()
report_generator = ReportGenerator()

# Inicializar LLM provider
llm_provider = get_llm_provider(
    provider_name=settings.LLM_PROVIDER,
    groq_api_key=settings.GROQ_API_KEY,
    ollama_url=settings.OLLAMA_BASE_URL,
    ollama_model=settings.OLLAMA_MODEL
)

processor = DocumentProcessor(process_settings, llm_provider)


# Sync fields from DB to ProcessorSettings on startup
def _sync_fields_from_db():
    """Load fields from database into ProcessorSettings."""
    process_settings.clear_fields()
    for field in fields_db.get_all():
        try:
            process_settings.create_field(field)
        except ValueError:
            pass  # Field already exists

_sync_fields_from_db()


# =====================
# ENDPOINTS DE PROCESOS
# =====================

@router.get("/processes", response_model=APIResponse)
async def list_processes(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Lista todos los procesos realizados."""
    try:
        process_list = db.get_all_processes(limit=limit, offset=offset)
        total = db.get_total_count()
        
        return APIResponse.ok(
            message=f"Se encontraron {total} procesos",
            data={
                "processes": process_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error listando procesos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/{process_id}", response_model=APIResponse)
async def get_process(process_id: str):
    """Obtiene un proceso específico por ID."""
    process = db.get_process(process_id)
    
    if process:
        return APIResponse.ok(message="Proceso encontrado", data=process)
    
    raise HTTPException(status_code=404, detail="Proceso no encontrado")


# =====================
# ENDPOINTS DE UPLOAD
# =====================

@router.post("/upload", response_model=APIResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Sube y procesa un archivo.
    
    Formatos soportados: PDF, CSV, Excel (.xlsx), TXT, LOG
    """
    logger.info(f"Archivo recibido: {file.filename} ({file.content_type})")
    
    # Validar extensión
    from src.extractor.extractor import FileExtractor
    supported = FileExtractor.get_supported_extensions()
    
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Formatos válidos: {', '.join(supported)}"
        )
    
    try:
        # Leer archivo
        file_bytes = await file.read()
        
        # Validar tamaño
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo muy grande. Máximo: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Procesar
        result = processor.process_file(file_bytes, file.filename)
        
        # Guardar en DB
        db.add_process(result)
        
        return APIResponse.ok(
            message="Archivo procesado exitosamente",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando archivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# ENDPOINTS DE CAMPOS
# =====================

@router.get("/fields", response_model=APIResponse)
async def list_fields():
    """Lista todos los campos de extracción configurados."""
    fields = fields_db.get_all()
    return APIResponse.ok(
        message=f"{len(fields)} campos configurados",
        data={"fields": fields}
    )


@router.post("/fields", response_model=APIResponse)
async def create_field(field: ExtractionField):
    """Crea un nuevo campo de extracción."""
    try:
        # Guardar en base de datos
        created = fields_db.create(field.model_dump())
        # Sincronizar con ProcessorSettings
        try:
            process_settings.create_field(created)
        except ValueError:
            pass  # Field already in memory
        return APIResponse.ok(
            message=f"Campo '{field.name}' creado exitosamente",
            data=created
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/fields/{field_name}", response_model=APIResponse)
async def delete_field(field_name: str):
    """Elimina un campo de extracción."""
    if fields_db.delete(field_name):
        process_settings.delete_field(field_name)
        return APIResponse.ok(message=f"Campo '{field_name}' eliminado")
    raise HTTPException(status_code=404, detail="Campo no encontrado")


@router.delete("/fields", response_model=APIResponse)
async def delete_all_fields():
    """Elimina todos los campos de extracción configurados."""
    count = fields_db.delete_all()
    process_settings.clear_fields()
    return APIResponse.ok(message=f"{count} campos eliminados")


@router.put("/fields/{field_name}", response_model=APIResponse)
async def update_field(field_name: str, updates: dict):
    """Actualiza un campo de extracción."""
    if fields_db.update(field_name, updates):
        process_settings.update_field(field_name, updates)
        return APIResponse.ok(message=f"Campo '{field_name}' actualizado")
    raise HTTPException(status_code=404, detail="Campo no encontrado")


# =====================
# ENDPOINTS DE REPORTES
# =====================

@router.post("/reports/generate")
async def generate_report(config: ReportConfig):
    """
    Genera un reporte con los procesos realizados.
    
    Formatos: excel, csv, json
    """
    try:
        data = db.get_all_processes(limit=settings.MAX_REPORT_RECORDS)
        
        # Filtrar por rango de fechas si se especifica
        if config.date_range_start or config.date_range_end:
            filtered = []
            for proc in data:
                proc_date = datetime.fromisoformat(proc.get('processed_at', ''))
                if config.date_range_start and proc_date < config.date_range_start:
                    continue
                if config.date_range_end and proc_date > config.date_range_end:
                    continue
                filtered.append(proc)
            data = filtered
        
        # Generar reporte
        content = report_generator.generate(
            data=data,
            format=config.format,
            title=config.title,
            include_metadata=config.include_metadata
        )
        
        # Preparar respuesta
        content_types = {
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv',
            'json': 'application/json'
        }
        
        extensions = {'excel': 'xlsx', 'csv': 'csv', 'json': 'json'}
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_types[config.format],
            headers={
                "Content-Disposition": f"attachment; filename=reporte.{extensions[config.format]}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# ENDPOINTS DE ESTADO
# =====================

@router.get("/health")
async def health_check():
    """Health check del servicio."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }


@router.get("/info", response_model=APIResponse)
async def api_info():
    """Información de la API y configuración."""
    from src.extractor.extractor import FileExtractor
    
    return APIResponse.ok(
        message="API Document Processor",
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "supported_formats": FileExtractor.get_supported_extensions(),
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "llm_provider": settings.LLM_PROVIDER,
            "fields_configured": len(process_settings.get_fields())
        }
    )
