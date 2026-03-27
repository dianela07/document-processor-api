# Document Processor API

Plataforma de extracción automática de datos desde documentos utilizando modelos de lenguaje (LLM). Procesa archivos PDF, Excel, CSV y texto, extrayendo información estructurada de forma eficiente.

## Descripción

Document Processor es una solución completa para automatizar la extracción de datos de documentos empresariales. El sistema permite definir campos personalizados de extracción y utiliza inteligencia artificial para identificar y estructurar la información relevante.

### Caso de uso

Un analista necesita procesar múltiples documentos diariamente (facturas, reportes, logs) y extraer información específica. Esta aplicación automatiza todo el flujo:

1. **Subir archivo** → 2. **Procesar con LLM** → 3. **Extraer datos** → 4. **Generar reporte**

## Características

- **Múltiples formatos**: PDF, Excel (.xlsx, .xls), CSV, texto (.txt, .log)
- **Extracción inteligente**: Campos personalizables con tipos de datos (string, number, date, boolean)
- **Proveedores LLM flexibles**: Groq (gratuito), Ollama (local), Azure OpenAI
- **Generación de reportes**: Exportación a Excel, CSV y JSON
- **API RESTful**: Documentación automática con Swagger/OpenAPI
- **Interfaz web**: Frontend profesional con Streamlit

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   LLM Provider  │
│   (Streamlit)   │     │    (FastAPI)    │     │  (Groq/Ollama)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Procesador    │
                        │  de Documentos  │
                        └─────────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │ Extractor │   │    LLM    │   │  Reports  │
        │  (PDF,    │   │ Extractor │   │ Generator │
        │ Excel...) │   │           │   │           │
        └───────────┘   └───────────┘   └───────────┘
```

## Estructura del proyecto

```
document-processor-api/
├── backend/
│   └── src/
│       ├── main.py              # Punto de entrada FastAPI
│       ├── core/
│       │   ├── config.py        # Configuración centralizada
│       │   └── logging_config.py
│       ├── database/
│       │   ├── db.py            # Repositorios SQLite
│       │   └── models.py        # Modelos SQLAlchemy
│       ├── extractor/
│       │   └── extractor.py     # Extracción de contenido
│       ├── llm/
│       │   └── providers.py     # Proveedores LLM
│       ├── models/
│       │   └── schemas.py       # Modelos Pydantic
│       ├── processor/
│       │   └── processor.py     # Lógica de procesamiento
│       ├── reports/
│       │   └── generator.py     # Generación de reportes
│       └── routes/
│           └── api_routes.py    # Endpoints REST
├── frontend/
│   └── app.py                   # Interfaz Streamlit
├── requirements.txt
├── .env.example                 # Plantilla de configuración
└── README.md
```

## Requisitos

- Python 3.10+
- API Key de Groq (gratuita) o Ollama instalado localmente

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/document-processor-api.git
cd document-processor-api
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# Proveedor LLM: "groq", "ollama", "azure", "none"
LLM_PROVIDER=groq

# Groq (Recomendado - Gratuito)
# Obtén tu API key en: https://console.groq.com
GROQ_API_KEY=tu_api_key_aqui

# Ollama (Alternativa local)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2

# Configuración opcional
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

## Uso

### Iniciar el backend

```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

### Iniciar el frontend

```bash
cd frontend
streamlit run app.py
```

El frontend estará disponible en: http://localhost:8501

## API Endpoints

### Procesamiento de documentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Sube y procesa un archivo |
| `GET` | `/api/v1/processes` | Lista todos los procesos |
| `GET` | `/api/v1/processes/{id}` | Obtiene un proceso específico |

### Campos de extracción

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/fields` | Lista campos configurados |
| `POST` | `/api/v1/fields` | Crea un nuevo campo |
| `PUT` | `/api/v1/fields/{name}` | Actualiza un campo |
| `DELETE` | `/api/v1/fields/{name}` | Elimina un campo |
| `DELETE` | `/api/v1/fields` | Elimina todos los campos |

### Reportes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/reports/generate` | Genera reporte (Excel/CSV/JSON) |

### Estado

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check del servicio |
| `GET` | `/api/v1/info` | Información de la API |

## Ejemplo de uso con la API

### 1. Configurar campos de extracción

```bash
curl -X POST http://localhost:8000/api/v1/fields \
  -H "Content-Type: application/json" \
  -d '{
    "name": "numero_factura",
    "description": "Número único de la factura",
    "field_type": "string",
    "required": true
  }'
```

### 2. Procesar un documento

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@factura.pdf"
```

### 3. Generar reporte

```bash
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"format": "excel", "title": "Reporte de facturas"}' \
  --output reporte.xlsx
```

## Proveedores LLM soportados

### Groq (Recomendado)

Servicio gratuito con límites generosos. Usa modelos Llama optimizados.

1. Registrarse en [console.groq.com](https://console.groq.com)
2. Generar API key
3. Configurar en `.env`:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=tu_api_key
   ```

### Ollama (Local)

100% local y gratuito. Requiere instalación.

1. Instalar [Ollama](https://ollama.ai)
2. Descargar modelo: `ollama pull llama3.2`
3. Configurar en `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

### Azure OpenAI (Empresarial)

Para entornos corporativos con Azure.

```env
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=tu_key
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Formatos de archivo soportados

| Formato | Extensiones | Descripción |
|---------|-------------|-------------|
| PDF | `.pdf` | Extracción de texto de documentos |
| Excel | `.xlsx`, `.xls` | Lectura de hojas y celdas |
| CSV | `.csv` | Datos tabulares |
| Texto | `.txt`, `.log` | Archivos de texto plano y logs |

## Tecnologías

- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: Streamlit
- **LLM**: OpenAI SDK (compatible con Groq), Ollama
- **Extracción**: PyPDF2, openpyxl
- **Reportes**: openpyxl, pandas

## Licencia

MIT License

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de crear un pull request.
