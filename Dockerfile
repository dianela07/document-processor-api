FROM python:3.11-slim

WORKDIR /app

# Copiar requirements del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/src ./src

# Crear directorio para datos
RUN mkdir -p /app/data

# Puerto de Hugging Face Spaces
EXPOSE 7860

# Variables de entorno por defecto
ENV LLM_PROVIDER=groq

# Iniciar servidor
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
