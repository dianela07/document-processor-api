"""
Proveedores de LLM - Soporte para múltiples servicios.
Incluye opciones GRATUITAS: Groq, Ollama
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging
import json

from src.core.config import settings

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Clase base para proveedores de LLM."""
    
    @abstractmethod
    def get_response(self, prompt: str) -> str:
        """Obtiene respuesta del modelo."""
        pass
    
    def extract_json(self, response: str, expected_keys: list[str]) -> dict:
        """Extrae JSON de la respuesta del modelo."""
        # Buscar JSON en la respuesta
        try:
            # Intentar parsear directamente
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Buscar bloques de código JSON
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Buscar cualquier JSON válido
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning("No se pudo extraer JSON de la respuesta")
        return {key: None for key in expected_keys}


class GroqProvider(BaseLLMProvider):
    """
    Proveedor Groq - GRATUITO con límites generosos.
    https://console.groq.com - Obtén tu API key gratis
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        logger.info(f"Groq Provider inicializado con modelo: {model}")
    
    def get_response(self, prompt: str) -> str:
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error en Groq: {e}")
            raise


class OllamaProvider(BaseLLMProvider):
    """
    Proveedor Ollama - 100% LOCAL y GRATUITO.
    https://ollama.ai - Instala y ejecuta modelos localmente
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        logger.info(f"Ollama Provider inicializado - URL: {base_url}, Modelo: {model}")
    
    def get_response(self, prompt: str) -> str:
        try:
            import httpx
            
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")
            raise


class AzureOpenAIProvider(BaseLLMProvider):
    """
    Proveedor Azure OpenAI - DE PAGO.
    """
    
    def __init__(self, api_key: str, endpoint: str, api_version: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.api_version = api_version
        self.model = model
        logger.info(f"Azure OpenAI Provider inicializado con modelo: {model}")
    
    def get_response(self, prompt: str) -> str:
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.LLM_MAX_TOKENS
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error en Azure OpenAI: {e}")
            raise


class MockProvider(BaseLLMProvider):
    """
    Proveedor Mock para testing - No requiere API.
    Útil para desarrollo y pruebas.
    """
    
    def __init__(self):
        logger.info("Mock Provider inicializado - Respuestas simuladas")
    
    def get_response(self, prompt: str) -> str:
        # Simular extracción básica
        return json.dumps({
            "campo_ejemplo": "valor_simulado",
            "fecha": "2026-03-25",
            "total": 0.0
        })


def get_llm_provider(
    provider_name: str,
    groq_api_key: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
    ollama_model: str = "llama3.2",
    azure_key: Optional[str] = None,
    azure_endpoint: Optional[str] = None,
    azure_version: str = "2024-02-15-preview"
) -> BaseLLMProvider:
    """
    Factory para obtener el proveedor de LLM configurado.
    
    Args:
        provider_name: "groq", "ollama", "azure", o "mock"
        
    Returns:
        Instancia del proveedor configurado
    """
    providers = {
        "groq": lambda: GroqProvider(groq_api_key, "llama-3.1-8b-instant"),
        "ollama": lambda: OllamaProvider(ollama_url, ollama_model),
        "azure": lambda: AzureOpenAIProvider(azure_key, azure_endpoint, azure_version),
        "mock": lambda: MockProvider(),
        "none": lambda: MockProvider()
    }
    
    if provider_name not in providers:
        logger.warning(f"Proveedor '{provider_name}' no reconocido, usando Mock")
        return MockProvider()
    
    return providers[provider_name]()
