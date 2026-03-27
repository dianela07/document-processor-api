"""
Configuración de logging profesional.
Demuestra: Buenas prácticas, trazabilidad, debugging.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log") -> None:
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta al archivo de logs
    """
    # Crear directorio de logs si no existe
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Formato del log
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar el logger raíz
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Handler para consola
            logging.StreamHandler(sys.stdout),
            # Handler para archivo
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Sistema de logging inicializado - Nivel: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del módulo/componente
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class ProcessLogger:
    """Logger especializado para tracking de procesos."""
    
    def __init__(self, process_id: str):
        self.process_id = process_id
        self.logger = logging.getLogger(f"process.{process_id}")
        self.start_time = datetime.now()
    
    def start(self, filename: str) -> None:
        self.logger.info(f"[{self.process_id}] Iniciando procesamiento de: {filename}")
    
    def step(self, step_name: str, details: str = "") -> None:
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"[{self.process_id}] {step_name} ({elapsed:.2f}s) {details}")
    
    def complete(self, result_summary: str = "") -> None:
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"[{self.process_id}] Completado en {elapsed:.2f}s - {result_summary}")
    
    def error(self, error_msg: str) -> None:
        self.logger.error(f"[{self.process_id}] ERROR: {error_msg}")
