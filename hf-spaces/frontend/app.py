"""
Frontend Streamlit - Document Processor
Sistema de extracción automática de datos de documentos.
Versión para Hugging Face Spaces.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Document Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de API - Lee de secrets de HF o variable de entorno
def get_api_url():
    # Intentar leer de st.secrets (HF Spaces)
    try:
        return st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000/api/v1"))
    except Exception:
        return os.getenv("API_URL", "http://localhost:8000/api/v1")

API_URL = get_api_url()

# Cargar Font Awesome (fuente externa)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Icon helpers */
    .fas, .far, .fab {
        vertical-align: middle;
        margin-right: 8px;
    }
    
    /* Header principal */
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.25rem;
    }
    .app-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
    }
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .sub-header strong {
        color: #4361ee;
    }
    
    /* Cards y contenedores */
    .info-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #4361ee;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .status-connected {
        color: #198754;
        font-weight: 500;
    }
    .status-disconnected {
        color: #dc3545;
        font-weight: 500;
    }
    
    /* Mejoras generales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 4px 4px 0 0;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Métricas personalizadas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #4361ee;
    }
    
    /* Botones más elegantes */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #dee2e6;
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_api_info():
    """Obtiene información de la API."""
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        return response.json() if response.ok else None
    except requests.exceptions.RequestException:
        return None


def upload_file(file):
    """Sube un archivo a la API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_URL}/upload", files=files, timeout=60)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_processes():
    """Obtiene la lista de procesos."""
    try:
        response = requests.get(f"{API_URL}/processes", timeout=10)
        return response.json() if response.ok else {"data": {"processes": []}}
    except requests.exceptions.RequestException:
        return {"data": {"processes": []}}


def get_fields():
    """Obtiene los campos configurados."""
    try:
        response = requests.get(f"{API_URL}/fields", timeout=5)
        return response.json() if response.ok else {"data": {"fields": []}}
    except requests.exceptions.RequestException:
        return {"data": {"fields": []}}


def create_field(field_data):
    """Crea un nuevo campo."""
    try:
        response = requests.post(f"{API_URL}/fields", json=field_data, timeout=5)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_field(field_name):
    """Elimina un campo."""
    try:
        response = requests.delete(f"{API_URL}/fields/{field_name}", timeout=5)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_all_fields():
    """Elimina todos los campos configurados."""
    try:
        response = requests.delete(f"{API_URL}/fields", timeout=5)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def generate_report(format_type="excel"):
    """Genera un reporte."""
    try:
        response = requests.post(
            f"{API_URL}/reports/generate",
            json={"format": format_type, "title": "Reporte de Procesos"},
            timeout=30
        )
        return response.content if response.ok else None
    except requests.exceptions.RequestException:
        return None


# ==================
# INTERFAZ PRINCIPAL
# ==================

# Header
st.markdown('''
<div class="app-header">
    <div class="app-icon"><i class="fas fa-file-alt"></i></div>
    <h1 class="main-header">Document Processor</h1>
</div>
<p class="sub-header">
    Plataforma para <strong>extracción automática de datos</strong> desde documentos. 
    Procesa archivos PDF, Excel, CSV y texto.
</p>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Configuración")
    
    # Verificar conexión con API
    api_info = get_api_info()
    if api_info and api_info.get("success"):
        st.markdown('<span class="status-connected">● Conectado</span>', unsafe_allow_html=True)
        info = api_info.get("data", {})
        st.caption(f"v{info.get('version', 'N/A')} · {info.get('llm_provider', 'N/A').upper()}")
        
        formats = info.get('supported_formats', [])
        st.caption(f"Formatos: {', '.join([f.upper() for f in formats])}")
    else:
        st.markdown('<span class="status-disconnected">● Desconectado</span>', unsafe_allow_html=True)
        st.caption(f"API: {API_URL}")
    
    st.divider()
    
    # Configuración de campos
    st.markdown("### Campos de extracción")
    
    fields_response = get_fields()
    fields = fields_response.get("data", {}).get("fields", [])
    
    if fields:
        for field in fields:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(field.get('name'))
            with col2:
                if st.button("×", key=f"del_{field.get('name')}", help="Eliminar campo"):
                    delete_field(field.get('name'))
                    st.rerun()
        
        # Botón para eliminar todos los campos
        if st.button("Eliminar todos", type="secondary", use_container_width=True):
            result = delete_all_fields()
            if result.get("success"):
                st.rerun()
    else:
        st.caption("Sin campos configurados")
    
    st.divider()
    
    # Añadir nuevo campo
    with st.expander("Agregar campo"):
        new_name = st.text_input("Nombre", placeholder="ej: total_factura")
        new_desc = st.text_input("Descripción", placeholder="ej: Monto total de la factura")
        new_type = st.selectbox("Tipo de dato", ["string", "number", "date", "boolean"])
        
        if st.button("Crear", type="primary", use_container_width=True):
            if new_name and new_desc:
                result = create_field({
                    "name": new_name,
                    "description": new_desc,
                    "field_type": new_type,
                    "required": True
                })
                if result.get("success"):
                    st.success("Campo creado correctamente")
                    st.rerun()
                else:
                    st.error(result.get("message", "Error al crear campo"))
            else:
                st.warning("Completa todos los campos requeridos")


# Tabs principales
tab1, tab2, tab3 = st.tabs(["Procesamiento", "Historial", "Reportes"])

# ==================
# TAB 1: SUBIR ARCHIVO
# ==================
with tab1:
    st.markdown('<h3><i class="fas fa-upload" style="color: #4361ee;"></i>Procesar documento</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Arrastra o selecciona un archivo",
            type=["pdf", "csv", "xlsx", "xls", "txt", "log"],
            help="PDF, CSV, Excel (.xlsx, .xls), Texto (.txt, .log)"
        )
        
        if uploaded_file:
            file_size = uploaded_file.size / 1024
            size_label = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.2f} MB"
            
            st.markdown(f"""
            <div class="info-card">
                <strong>{uploaded_file.name}</strong><br>
                <small style="color: #6c757d;">{size_label} · {uploaded_file.type}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Procesar archivo", type="primary", use_container_width=True):
                with st.spinner("Procesando..."):
                    result = upload_file(uploaded_file)
                
                if result.get("success"):
                    st.success("Documento procesado correctamente")
                    
                    # Mostrar resultados
                    data = result.get("data", {})
                    
                    st.markdown("#### Datos extraídos")
                    extracted = data.get("extracted_data", {})
                    
                    if extracted:
                        # Mostrar como tabla
                        df = pd.DataFrame([extracted])
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # JSON expandible
                        with st.expander("Ver datos en formato JSON"):
                            st.json(extracted)
                    else:
                        st.info("No se extrajeron datos. Configura los campos de extracción en la barra lateral.")
                    
                    # Metadatos
                    with st.expander("Metadatos del documento"):
                        st.json(data.get("metadata", {}))
                else:
                    st.error(f"Error: {result.get('message', 'Error desconocido')}")
    
    with col2:
        st.markdown("#### Guía rápida")
        st.markdown("""
        1. Define los campos a extraer en la barra lateral
        2. Sube tu documento (PDF, CSV, Excel o texto)
        3. El sistema extraerá automáticamente los datos
        4. Exporta los resultados desde Reportes
        """)
        
        st.markdown("#### Ejemplo de campos")
        st.code("""numero_factura: Número único
fecha: Fecha de emisión  
total: Importe total
proveedor: Nombre del emisor""", language=None)


# ==================
# TAB 2: HISTORIAL
# ==================
with tab2:
    st.markdown('<h3><i class="fas fa-history" style="color: #4361ee;"></i>Historial de procesos</h3>', unsafe_allow_html=True)
    
    col_refresh, col_spacer = st.columns([1, 5])
    with col_refresh:
        if st.button("Actualizar", key="refresh_history"):
            st.rerun()
    
    processes_response = get_processes()
    processes = processes_response.get("data", {}).get("processes", [])
    
    if processes:
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", len(processes))
        with col2:
            completed = len([p for p in processes if p.get("status") == "completed"])
            st.metric("Completados", completed)
        with col3:
            errors = len([p for p in processes if p.get("status") == "error"])
            st.metric("Con errores", errors)
        
        st.divider()
        
        # Convertir a DataFrame
        df = pd.DataFrame(processes)
        
        # Tabla de procesos
        if 'extracted_data' in df.columns:
            df['extracted_data'] = df['extracted_data'].apply(
                lambda x: json.dumps(x, ensure_ascii=False)[:50] + "..." if isinstance(x, dict) else str(x)
            )
        
        # Renombrar columnas para mejor visualización
        column_labels = {
            'filename': 'Archivo',
            'status': 'Estado', 
            'processed_at': 'Fecha de proceso'
        }
        
        display_cols = ['filename', 'status', 'processed_at']
        available_cols = [c for c in display_cols if c in df.columns]
        
        display_df = df[available_cols].copy() if available_cols else df.copy()
        display_df.columns = [column_labels.get(c, c) for c in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Detalle de proceso seleccionado
        st.markdown("#### Detalle del proceso")
        filenames = df['filename'].tolist() if 'filename' in df.columns else []
        selected = st.selectbox("Seleccionar proceso", filenames, label_visibility="collapsed")
        
        if selected:
            process = next((p for p in processes if p.get('filename') == selected), None)
            if process:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Datos extraídos**")
                    st.json(process.get('extracted_data', {}))
                with col2:
                    st.markdown("**Metadatos**")
                    st.json(process.get('metadata', {}))
    else:
        st.info("No hay procesos registrados. Sube un archivo para comenzar.")


# ==================
# TAB 3: REPORTES
# ==================
with tab3:
    st.markdown('<h3><i class="fas fa-download" style="color: #4361ee;"></i>Exportar datos</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Formato")
        
        report_format = st.radio(
            "Selecciona el formato",
            ["excel", "csv", "json"],
            format_func=lambda x: {"excel": "Excel (.xlsx)", "csv": "CSV (.csv)", "json": "JSON (.json)"}[x],
            label_visibility="collapsed"
        )
        
        st.markdown("")  # Espaciado
        
        if st.button("Generar reporte", type="primary", use_container_width=True):
            with st.spinner("Generando..."):
                content = generate_report(report_format)
            
            if content:
                # Extensiones y MIME types
                ext_map = {"excel": "xlsx", "csv": "csv", "json": "json"}
                mime_map = {
                    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "csv": "text/csv",
                    "json": "application/json"
                }
                
                filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext_map[report_format]}"
                
                st.download_button(
                    label="Descargar archivo",
                    data=content,
                    file_name=filename,
                    mime=mime_map[report_format],
                    use_container_width=True
                )
                st.success("Reporte generado correctamente")
            else:
                st.error("No se pudo generar el reporte")
    
    with col2:
        st.markdown("#### Vista previa")
        
        processes_response = get_processes()
        processes = processes_response.get("data", {}).get("processes", [])
        
        if processes:
            preview_df = pd.DataFrame(processes[:5])
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando 5 de {len(processes)} registros totales")
        else:
            st.info("No hay datos disponibles para exportar")


# Footer
st.divider()
st.caption("Document Processor · FastAPI + Streamlit")
