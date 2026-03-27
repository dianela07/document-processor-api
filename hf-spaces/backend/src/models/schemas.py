"""
Modelos Pydantic para validación de datos.
Demuestra: Buenas prácticas, tipado, validación robusta.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class FieldType(str, Enum):
    """Tipos de datos soportados para campos de extracción."""
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    LIST = "list"


class ExtractionField(BaseModel):
    """Define un campo a extraer del documento."""
    name: str = Field(..., min_length=1, max_length=50, description="Nombre del campo")
    description: str = Field(..., min_length=1, max_length=200, description="Descripción del campo")
    field_type: FieldType = Field(default=FieldType.STRING, description="Tipo de dato esperado")
    required: bool = Field(default=True, description="Si el campo es obligatorio")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validar que el nombre sea un identificador válido."""
        if not v.replace('_', '').isalnum():
            raise ValueError('El nombre solo puede contener letras, números y guiones bajos')
        return v.lower().strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "total_factura",
                "description": "Monto total de la factura",
                "field_type": "number",
                "required": True
            }
        }


class ProcessRequest(BaseModel):
    """Solicitud de procesamiento de archivo."""
    filename: str
    content_type: str
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        allowed_types = [
            'application/pdf',
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/plain'
        ]
        if v not in allowed_types:
            raise ValueError(f'Tipo de contenido no soportado: {v}')
        return v


class ProcessResult(BaseModel):
    """Resultado del procesamiento de un documento."""
    id: str = Field(..., description="ID único del proceso")
    filename: str
    processed_at: datetime
    status: str = Field(default="completed")
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "proc_20260325_001",
                "filename": "factura.pdf",
                "processed_at": "2026-03-25T10:30:00",
                "status": "completed",
                "extracted_data": {
                    "total": 1500.00,
                    "fecha": "2026-03-20"
                },
                "metadata": {
                    "pages": 2,
                    "processing_time_ms": 1200
                }
            }
        }


class ReportConfig(BaseModel):
    """Configuración para generación de reportes."""
    title: str = Field(default="Reporte de Procesamiento")
    include_metadata: bool = Field(default=True)
    format: str = Field(default="excel", pattern="^(excel|csv|json)$")
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class APIResponse(BaseModel):
    """Respuesta estándar de la API."""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[list[str]] = None
    
    @classmethod
    def ok(cls, message: str, data: Any = None) -> "APIResponse":
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error(cls, message: str, errors: list[str] = None) -> "APIResponse":
        return cls(success=False, message=message, errors=errors or [message])
