"""
Procesador principal de documentos.
Integra extractor, LLM y generador de reportes.
"""
from datetime import datetime, timezone
from typing import Optional
import logging
import uuid

from src.extractor.extractor import FileExtractor
from src.llm.providers import BaseLLMProvider, get_llm_provider
from src.core.config import settings
from src.core.logging_config import ProcessLogger

logger = logging.getLogger(__name__)


class ProcessorSettings:
    """Gestiona los campos configurados para extracción."""
    
    def __init__(self):
        self._fields: list[dict] = []
    
    def create_field(self, field: dict) -> None:
        """Añade un nuevo campo a extraer."""
        # Validar que tenga las propiedades mínimas
        if 'name' not in field:
            raise ValueError("El campo debe tener un 'name'")
        
        # Evitar duplicados
        if any(f['name'] == field['name'] for f in self._fields):
            raise ValueError(f"El campo '{field['name']}' ya existe")
        
        self._fields.append(field)
        logger.info(f"Campo creado: {field['name']}")
    
    def delete_field(self, field_name: str) -> bool:
        """Elimina un campo por nombre."""
        original_len = len(self._fields)
        self._fields = [f for f in self._fields if f.get('name') != field_name]
        deleted = len(self._fields) < original_len
        if deleted:
            logger.info(f"Campo eliminado: {field_name}")
        return deleted
    
    def update_field(self, field_name: str, updates: dict) -> bool:
        """Actualiza un campo existente."""
        for field in self._fields:
            if field.get('name') == field_name:
                field.update(updates)
                logger.info(f"Campo actualizado: {field_name}")
                return True
        return False
    
    def get_fields(self) -> list[dict]:
        """Retorna todos los campos configurados."""
        return self._fields.copy()
    
    def clear_fields(self) -> None:
        """Elimina todos los campos."""
        self._fields.clear()
        logger.info("Todos los campos eliminados")


class DocumentProcessor:
    """
    Procesador de documentos con extracción inteligente.
    
    Pipeline:
    1. Extrae texto del archivo (PDF, CSV, Excel, etc.)
    2. Envía al LLM para extraer entidades
    3. Retorna datos estructurados
    """
    
    EXTRACTION_PROMPT = """Extrae los siguientes campos del texto proporcionado.

Campos a extraer (formato: nombre - descripción - tipo):
{fields}

Texto del documento:
{text}

IMPORTANTE:
- Responde SOLO con un JSON válido
- Usa los nombres de campo exactos como claves
- Si no encuentras un valor, usa null
- Para números, usa valores numéricos sin símbolos de moneda
- Para fechas, usa formato YYYY-MM-DD

JSON:"""

    def __init__(
        self,
        settings: ProcessorSettings,
        llm_provider: Optional[BaseLLMProvider] = None
    ):
        self.settings = settings
        self.extractor = FileExtractor()
        
        # Inicializar proveedor LLM
        if llm_provider:
            self.llm = llm_provider
        else:
            self.llm = get_llm_provider(
                provider_name=settings.LLM_PROVIDER if hasattr(settings, 'LLM_PROVIDER') else "mock"
            )
    
    def process_file(self, file_bytes: bytes, filename: str) -> dict:
        """
        Procesa un archivo completo.
        
        Args:
            file_bytes: Contenido del archivo
            filename: Nombre del archivo
            
        Returns:
            Diccionario con los datos extraídos y metadatos
        """
        process_id = f"proc_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        proc_logger = ProcessLogger(process_id)
        
        proc_logger.start(filename)
        
        try:
            # 1. Extraer contenido del archivo
            proc_logger.step("Extracción", f"Formato detectado")
            extraction_result = self.extractor.extract(file_bytes, filename)
            content = extraction_result['content']
            file_metadata = extraction_result['metadata']
            
            # 2. Extraer entidades con LLM
            fields = self.settings.get_fields()
            
            if fields:
                proc_logger.step("LLM", f"Extrayendo {len(fields)} campos")
                extracted_data = self._extract_with_llm(content, fields)
            else:
                proc_logger.step("LLM", "Sin campos configurados - solo extracción de texto")
                extracted_data = {"raw_text": content[:500] + "..." if len(content) > 500 else content}
            
            # 3. Preparar resultado
            result = {
                "id": process_id,
                "filename": filename,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "extracted_data": extracted_data,
                "metadata": {
                    **file_metadata,
                    "format": extraction_result['format'],
                    "extension": extraction_result.get('extension', ''),
                    "fields_extracted": len(fields)
                }
            }
            
            proc_logger.complete(f"{len(extracted_data)} campos extraídos")
            return result
            
        except Exception as e:
            proc_logger.error(str(e))
            return {
                "id": process_id,
                "filename": filename,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(e),
                "extracted_data": {},
                "metadata": {}
            }
    
    def _extract_with_llm(self, text: str, fields: list[dict]) -> dict:
        """Usa el LLM para extraer campos del texto."""
        # Formatear campos para el prompt
        fields_text = "\n".join([
            f"- {f.get('name')}: {f.get('description', 'Sin descripción')} ({f.get('field_type', 'string')})"
            for f in fields
        ])
        
        # Limitar texto si es muy largo
        max_chars = settings.MAX_TEXT_LENGTH_FOR_LLM
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[texto truncado]..."
        
        prompt = self.EXTRACTION_PROMPT.format(fields=fields_text, text=text)
        
        response = self.llm.get_response(prompt)
        expected_keys = [f['name'] for f in fields]
        
        return self.llm.extract_json(response, expected_keys)
