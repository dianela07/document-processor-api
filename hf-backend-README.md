---
title: Document Processor API
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Document Processor API

FastAPI backend for automatic document data extraction using LLMs.

## Endpoints

- `GET /api/v1/info` - API information
- `POST /api/v1/upload` - Upload and process document
- `GET /api/v1/processes` - List all processes
- `POST /api/v1/fields` - Create extraction field
- `GET /api/v1/fields` - List all fields
- `GET /api/v1/reports/{format}` - Generate report (excel, csv, json)

## Configuration

Set `GROQ_API_KEY` in Space secrets for LLM functionality.
