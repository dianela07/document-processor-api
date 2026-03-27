"""
Frontend Streamlit - Document Processor
Sistema de extracción automática de datos de documentos.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Configuración de la página
st.set_page_config(
    page_title="Document Processor",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados + Iconos externos
st.markdown("""
<!-- Font Awesome & Material Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">

<style>
    /* Icon helpers */
    .fa, .fas, .far, .fab, .material-icons {
        vertical-align: middle;
    }
    .icon-sm { font-size: 0.9rem; }
    .icon-md { font-size: 1.1rem; }
    .icon-lg { font-size: 1.4rem; }
    .icon-primary { color: #4361ee; }
    .icon-success { color: #198754; }
    .icon-danger { color: #dc3545; }
    .icon-warning { color: #ffc107; }
    .icon-muted { color: #6c757d; }
    
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

# Configuración
API_URL = "http://localhost:8000/api/v1"


def get_api_info():
    """Obtiene información de la API."""
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        return response.json() if response.ok else None
    except:
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
    except:
        return {"data": {"processes": []}}


def get_fields():
    """Obtiene los campos configurados."""
    try:
        response = requests.get(f"{API_URL}/fields", timeout=5)
        return response.json() if response.ok else {"data": {"fields": []}}
    except:
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
    except:
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
    <i class="fas fa-robot icon-sm icon-primary"></i> Plataforma inteligente para <strong>extracción automática de datos</strong> desde documentos. 
    Procesa archivos PDF, Excel, CSV y texto, extrayendo información estructurada de forma eficiente.
</p>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h3><i class="fas fa-cog icon-sm icon-muted"></i> Configuración</h3>', unsafe_allow_html=True)
    
    # Verificar conexión con API
    api_info = get_api_info()
    if api_info and api_info.get("success"):
        st.markdown('<span class="status-connected"><i class="fas fa-circle icon-sm"></i> Conectado</span>', unsafe_allow_html=True)
        info = api_info.get("data", {})
        st.caption(f"Versión {info.get('version', 'N/A')} · {info.get('llm_provider', 'N/A').upper()}")
        
        # Mostrar formatos soportados de forma clara
        formats = info.get('supported_formats', [])
        formats_display = ", ".join([f.upper() for f in formats])
        st.caption(f"Formatos: {formats_display}")
    else:
        st.markdown('<span class="status-disconnected"><i class="fas fa-circle icon-sm"></i> Desconectado</span>', unsafe_allow_html=True)
        st.caption("Verifica que el backend esté corriendo en localhost:8000")
    
    st.divider()
    
    # Configuración de campos
    st.markdown('<h3><i class="fas fa-list-check icon-sm icon-muted"></i> Campos de extracción</h3>', unsafe_allow_html=True)
    
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
tab1, tab2, tab3 = st.tabs(["📤 Procesamiento", "📋 Historial", "📊 Reportes"])

# ==================
# TAB 1: SUBIR ARCHIVO
# ==================
with tab1:
    st.markdown('<h3><i class="fas fa-upload icon-md icon-primary"></i> Procesar documento</h3>', unsafe_allow_html=True)
    
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
                <i class="fas fa-file icon-md icon-primary"></i> <strong>{uploaded_file.name}</strong><br>
                <small style="color: #6c757d;"><i class="fas fa-weight-hanging icon-sm"></i> {size_label} · {uploaded_file.type}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Procesar archivo", type="primary", use_container_width=True):
                with st.spinner("Procesando..."):
                    result = upload_file(uploaded_file)
                
                if result.get("success"):
                    st.success("Documento procesado correctamente")
                    
                    # Mostrar resultados
                    data = result.get("data", {})
                    
                    st.markdown('<h4><i class="fas fa-table icon-sm icon-success"></i> Datos extraídos</h4>', unsafe_allow_html=True)
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
        st.markdown('<h4><i class="fas fa-lightbulb icon-sm icon-warning"></i> Guía rápida</h4>', unsafe_allow_html=True)
        st.markdown("""
        **1.** <i class="fas fa-list-check icon-sm"></i> Define los campos a extraer en la barra lateral
        
        **2.** <i class="fas fa-cloud-upload-alt icon-sm"></i> Sube tu documento (PDF, CSV, Excel o texto)
        
        **3.** <i class="fas fa-magic icon-sm"></i> El sistema extraerá automáticamente los datos configurados
        
        **4.** <i class="fas fa-download icon-sm"></i> Exporta los resultados desde la pestaña Reportes
        """, unsafe_allow_html=True)
        
        st.markdown('<h4><i class="fas fa-code icon-sm icon-muted"></i> Ejemplo de campos</h4>', unsafe_allow_html=True)
        st.code("""numero_factura: Número único
fecha: Fecha de emisión  
total: Importe total
proveedor: Nombre del emisor""", language=None)


# ==================
# TAB 2: HISTORIAL
# ==================
with tab2:
    st.markdown('<h3><i class="fas fa-history icon-md icon-primary"></i> Historial de procesos</h3>', unsafe_allow_html=True)
    
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
        st.markdown('<h4><i class="fas fa-info-circle icon-sm icon-primary"></i> Detalle del proceso</h4>', unsafe_allow_html=True)
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
    st.markdown('<h3><i class="fas fa-file-export icon-md icon-primary"></i> Exportar datos</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h4><i class="fas fa-file-archive icon-sm icon-muted"></i> Formato de exportación</h4>', unsafe_allow_html=True)
        
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
        st.markdown('<h4><i class="fas fa-eye icon-sm icon-muted"></i> Vista previa</h4>', unsafe_allow_html=True)
        
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
st.markdown(
    '<p style="text-align: center; color: #6c757d; font-size: 0.85rem;">'
    '<i class="fas fa-code icon-sm"></i> Document Processor · '
    '<i class="fab fa-python icon-sm"></i> FastAPI + Streamlit'
    '</p>',
    unsafe_allow_html=True
)
