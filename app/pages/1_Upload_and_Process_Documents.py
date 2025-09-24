# 1_Upload_and_Process_Documents.py

import streamlit as st
from security import get_login_manager
import os
import chromadb
# MODIFIED: Import our new utility functions
from utils import process_and_index_documents, process_and_index_documents_with_ocr 
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ... (keep all the CSS and page config functions as they are) ...
def inject_upload_css():
    """Inject custom CSS for the upload page"""
    
    css = f"""
    <style>
    /* Hide Streamlit elements */
    .stDeployButton {{display:none;}}
    .stDecoration {{display:none;}}
    #MainMenu {{display:none;}}
    header {{display:none;}}
    footer {{display:none;}}
    
    /* Main app container */
    .stApp {{
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #333333;
        min-height: 100vh;
    }}
    
    /* Page title */
    .page-title {{
        font-size: 2.5rem;
        font-weight: bold;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* Section cards */
    .section-card {{
        background: white;
        border: 2px solid #00D400;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 212, 0, 0.1);
    }}
    
    .section-title {{
        color: #00D400;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    /* Input styling */
    .stTextInput > div > div > input {{
        background: white !important;
        border: 2px solid #00D400 !important;
        border-radius: 10px !important;
        color: #333333 !important;
        padding: 1rem !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #00F400 !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 0, 0.2) !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: #888888 !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, #00D400, #00A300) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 0, 0.3) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 0, 0.4) !important;
        background: linear-gradient(135deg, #00F400, #00D400) !important;
    }}
    
    /* Delete button styling */
    [data-testid="stButton"]:has(button:contains("Eliminar")) button {{
        background: linear-gradient(135deg, #ff4444, #cc0000) !important;
    }}
    
    [data-testid="stButton"]:has(button:contains("Eliminar")) button:hover {{
        background: linear-gradient(135deg, #ff6666, #ff4444) !important;
    }}
    
    /* Home button styling */
    [data-testid="stButton"]:has(button:contains("Inicio")) button {{
        background: rgba(0, 212, 0, 0.1) !important;
        border: 2px solid #00D400 !important;
        color: #00D400 !important;
    }}
    
    [data-testid="stButton"]:has(button:contains("Inicio")) button:hover {{
        background: rgba(0, 212, 0, 0.2) !important;
    }}
    
    /* Logout button styling */
    [data-testid="stButton"]:has(button:contains("Cerrar")) button {{
        background: linear-gradient(135deg, #ff4444, #cc0000) !important;
        color: white !important;
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {{
        background: white !important;
        border: 2px solid #00D400 !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    
    .stSelectbox > div > div > div > div {{
        color: #333333 !important;
    }}
    
    /* File uploader styling */
    .stFileUploader > div {{
        background: rgba(0, 212, 0, 0.05) !important;
        border: 2px dashed #00D400 !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        text-align: center !important;
    }}
    
    .stFileUploader label {{
        color: #333333 !important;
    }}
    
    /* Success/Error messages */
    .stSuccess {{
        background: rgba(0, 212, 0, 0.1) !important;
        border: 1px solid #00D400 !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    
    .stError {{
        background: rgba(255, 68, 68, 0.1) !important;
        border: 1px solid #ff4444 !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    
    .stWarning {{
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid #ffc107 !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    
    .stInfo {{
        background: rgba(0, 212, 0, 0.1) !important;
        border: 1px solid #00D400 !important;
        border-radius: 10px !important;
        color: #333333 !important;
    }}
    
    /* Database list styling */
    .database-item {{
        background: rgba(0, 212, 0, 0.05);
        border: 1px solid #00D400;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #333333;
    }}
    
    /* Text color adjustments */
    .stMarkdown, .stText, p, div, span {{
        color: #333333 !important;
    }}
    
    /* User info styling */
    .user-info {{
        color: #00D400;
        font-weight: bold;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .section-card {{
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        .page-title {{
            font-size: 2rem;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
    page_title="Subir y procesar documentos",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_upload_css()

# Get the login manager
login_manager = get_login_manager()

# Check authentication status
if not login_manager.verify_session():
    st.error('Por favor, inicia sesión para acceder a esta página.')
    st.stop()

# User is authenticated - show the page content
name = st.session_state.get('name', '')

# Navigation header
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("🏠 Inicio", key="home_btn", help="Volver al inicio"):
        st.switch_page("app.py")
with col2:
    st.markdown('<h1 class="page-title">📁 Subir y Procesar Documentos</h1>', unsafe_allow_html=True)
with col3:
    # User info container
    with st.container():
        st.markdown(f"""
        <div style="
            background: white;
            border: 2px solid #00D400;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 212, 0, 0.1);
        ">
            <div style="color: #00D400; font-weight: bold; margin-bottom: 0.5rem;">
                Bienvenido, {name}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión", key="logout_button_upload", use_container_width=True):
            login_manager.logout()
            st.rerun()

# --- Initialize session state for configurations if not already done ---
if "config" not in st.session_state:
    st.session_state.config = {
        # Model Configuration
        "gpt_model": "gpt-5-mini",
        "embedding_model": "text-embedding-3-large",
        "temperature": 1.0,
        
        # FAISS Configuration
        "retrieval_method": "faiss_hybrid",
        "faiss_index_type": "auto",
        "top_k": 20,
        
        # System Prompt Configuration
        "system_prompt": """You are Maxwell, a talkative but precise financial-data assistant for an enterprise RAG system.
Your only knowledge source is the <context> block plus the <chat_history>. Do not use outside knowledge.

— Goals —
1) Answer the user's question strictly using the provided context and previous messages.
2) Be friendly and conversational, but keep numbers, parties, and dates exact.
3) If the context is insufficient or conflicting, say so clearly and explain what to provide next.

— Data domain you work with —
Bank statements, invoices, receipts, payments, wire confirmations, client registries/CRMs, contracts, loan schedules, and related metadata.

— How to think —
- Ground every statement in the context. Never invent clients, balances, dates, rates, or terms.
- If multiple documents disagree, present the differing values side-by-side and cite their sources.
- Prefer concise lists or compact Markdown tables for multiple items; otherwise, short paragraphs are fine.
- When listing many items, show the top 20 and state how many were found in total.
- Use ISO dates (YYYY-MM-DD). Show currency codes if present (e.g., USD, EUR, ARS).

— Behaviors for common intents —
• "what can you do?" → Briefly describe tasks you can perform on this dataset (e.g., list clients present in context, summarize accounts and balances, trace payments, extract contract/loan terms, find overdue invoices), and give 3–5 example queries. Do not claim capabilities unrelated to data types in context.
• "what clients we have registered?" → Return unique client names/IDs found in context. Include any available fields (e.g., legal_name, client_id, accounts_count, invoices_count). Add a Sources section.
• "which of them have loans?" → Return only clients with loans. For each, show key fields available (loan_id, principal, current_balance, interest_rate, status, origination_date, maturity_date). Add Sources.
• "details about a specific document or client" → Provide the requested details (e.g., totals, balances, terms, parties, dates). If multiple matches exist, summarize each briefly. Always include Sources.

— What NOT to do —
- Don't answer with knowledge not supported by context.
- Don't guess unknown fields; write "not found in provided data".
- Don't expose chain-of-thought; give conclusions and the minimal reasoning needed.

— If context is missing/empty —
Say you can't answer from the provided data and ask for the exact thing needed (file name, date range, client ID, document type).

<chat_history>
{chat_history}
</chat_history>

<context>
{context}
</context>

User question:
{question}

— Output format —
1) Start with a direct answer.
2) If listing items, use a compact Markdown table with clear column headers when helpful.
3) End with a "Sources" section listing filenames/ids and, if available, page/section references used.
4) If the answer is partial or blocked by missing data, state that explicitly and ask for the minimal follow-up needed.""",
        
        # Document Summarization Prompts
        "document_summary_prompt": """Analiza el siguiente documento completo y crea un resumen estructurado en español que incluya:

1. RESUMEN GENERAL: Una descripción concisa del contenido y propósito del documento
2. PERSONAS MENCIONADAS: Nombres de personas, autores, firmantes, o individuos relevantes
3. NÚMEROS DE IDENTIFICACIÓN: DNI, NIE, números de expediente, códigos, referencias, etc.
4. FECHAS IMPORTANTES: Fechas de emisión, vencimiento, eventos mencionados
5. ENTIDADES Y ORGANIZACIONES: Empresas, instituciones, departamentos mencionados
6. CONCEPTOS CLAVE: Términos técnicos, productos, servicios, o temas principales
7. DATOS FINANCIEROS: Montos, precios, presupuestos, si aplica
8. UBICACIONES: Direcciones, ciudades, países mencionados

Documento: {source_file}
Contenido:
---
{document_content}
---

Responde en formato estructurado y conciso, enfocándote en información que sea útil para búsquedas y recuperación de información.""",

        "short_summary_prompt": "Resume en español el siguiente documento en 2-3 oraciones concisas, manteniendo términos clave y nombres importantes:\n\nDocumento: {source_file}\n\n---\n\n{document_content}"
    }

# --- ChromaDB Client Initialization ---
CHROMA_DB_PATH = "./chroma_db"

@st.cache_resource
def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

client = get_chroma_client()

# Get collections data first
try:
    collections = client.list_collections()
except Exception as e:
    st.error(f"Error conectando a ChromaDB: {e}")
    collections = []

# --- Main content in columns (Create and Delete) ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    # --- Create New Collection Section ---
    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            🆕 Crear Nueva Base de Datos
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    new_collection_name = st.text_input(
        "Nombre para la nueva base de datos:", 
        key="new_collection_name",
        placeholder="Ej: documentos_empresa_2024"
    )
    
    if st.button("✨ Crear Base de Datos", key="create_db", use_container_width=True):
        if new_collection_name:
            try:
                client.create_collection(name=new_collection_name)
                st.success(f"¡Base de datos '{new_collection_name}' creada exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al crear la base de datos: {e}")
        else:
            st.warning("Por favor, ingresa un nombre para la base de datos.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # --- Delete Collection Section ---
    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            🗑️ Eliminar Base de Datos
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if collections:
        collection_names = [c.name for c in collections]
        selected_collection_to_delete = st.selectbox(
            "Selecciona base de datos a eliminar:", 
            collection_names, 
            key="delete_collection_select"
        )
        
        st.warning("⚠️ **Advertencia**: Eliminar una base de datos removerá permanentemente todos los documentos y no se puede deshacer!")
        
        confirmation_text = st.text_input(
            f"Escribe '{selected_collection_to_delete}' para confirmar:",
            key="delete_confirmation",
            placeholder="Confirma el nombre aquí..."
        )
        
        if st.button("🗑️ Eliminar Base de Datos", key="delete_db", use_container_width=True):
            if confirmation_text == selected_collection_to_delete:
                try:
                                    # Note: No more pickle files to delete - ChromaDB handles all storage

                    client.delete_collection(name=selected_collection_to_delete)
                    st.success(f"¡Base de datos '{selected_collection_to_delete}' eliminada exitosamente!")
                    st.session_state.delete_confirmation = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar la base de datos: {e}")
            else:
                st.error("Por favor, escribe el nombre exacto de la base de datos para confirmar.")
    else:
        st.info("No hay bases de datos disponibles para eliminar.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- File Upload Section (Full Width) ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        📤 Subir y Procesar Documentos
    </div>
</div>
""", unsafe_allow_html=True)

if not collections:
    st.warning("Por favor, crea una base de datos vectorial primero.")
    selected_collection = None
else:
    collection_names = [c.name for c in collections]
    selected_collection = st.selectbox(
        "Selecciona la base de datos donde subir los archivos:", 
        collection_names,
        help="Los documentos se almacenarán en la base de datos seleccionada"
    )

# NEW: Add OCR processing option
use_ocr = st.checkbox(
    "🔍 Usar OCR avanzado para documentos PDF y Word",
    value=True,
    help="El OCR avanzado proporciona mejor extracción de texto y chunking automático. Recomendado para PDFs y documentos Word."
)


# NEW: Add a dropdown to select the document type for intelligent chunking
doc_type = st.selectbox(
    "Selecciona el tipo de documento para un procesamiento optimizado:",
    ["General", "Contract", "Form"],
    key="doc_type_select",
    help="Elegir el tipo correcto mejora la forma en que se divide y entiende el documento (solo para procesamiento tradicional)."
)

# File uploader with better styling
st.markdown("**Selecciona archivos para procesar:**")
uploaded_files = st.file_uploader(
    "Arrastra archivos aquí o haz clic para seleccionar",
    type=["pdf", "txt", "docx", "csv", "xls", "xlsx", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Formatos soportados: PDF, TXT, DOCX, CSV, XLS, XLSX, PNG, JPG, JPEG. OCR soporta: PDF, PNG, JPG, JPEG y convierte DOCX automáticamente."
)

# Process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Procesar Archivos Subidos", key="process_files", use_container_width=True):
        if selected_collection and uploaded_files:
            # MODIFIED: Use OCR-enhanced processing logic
            try:
                processing_method = "OCR avanzado" if use_ocr else "tradicional"
                with st.spinner(f"Paso 1/3: Procesando {len(uploaded_files)} archivos con método {processing_method}..."):
                    if use_ocr:
                        enriched_chunks, num_chunks = process_and_index_documents_with_ocr(
                            uploaded_files=uploaded_files,
                            collection_name=selected_collection,
                            doc_type=doc_type,
                            config=st.session_state.config,
                            chroma_path=CHROMA_DB_PATH,
                            use_ocr=True
                        )
                    else:
                        enriched_chunks, num_chunks = process_and_index_documents(
                            uploaded_files=uploaded_files,
                            collection_name=selected_collection,
                            doc_type=doc_type,
                            config=st.session_state.config,
                            chroma_path=CHROMA_DB_PATH
                        )
                    st.info(f"Documentos procesados y enriquecidos en {num_chunks} fragmentos usando método {processing_method}.")
                
                with st.spinner("Paso 2/3: Inicializando modelo de embeddings..."):
                    config = st.session_state.config
                    embedding_model_name = config["embedding_model"]
                    st.info(f"Usando modelo de embeddings: {embedding_model_name}")

                    if "openai" in embedding_model_name or "text-embedding" in embedding_model_name:
                        if not os.environ.get("OPENAI_API_KEY"):
                            st.error("Variable de entorno OPENAI_API_KEY no configurada.")
                            st.stop()
                        embeddings = OpenAIEmbeddings(model=embedding_model_name)
                    else:
                        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

                with st.spinner(f"Paso 3/3: Almacenando embeddings en la base de datos '{selected_collection}'..."):
                    vectorstore = Chroma.from_documents(
                        documents=enriched_chunks, # Use the enriched chunks
                        embedding=embeddings,
                        collection_name=selected_collection,
                        persist_directory=CHROMA_DB_PATH,
                    )
                    vectorstore.persist()

                st.success(f"¡{len(uploaded_files)} archivos procesados y almacenados exitosamente en '{selected_collection}'!")

            except Exception as e:
                st.error(f"Ocurrió un error durante el procesamiento: {e}")

        elif not selected_collection:
            st.warning("Por favor, selecciona una base de datos primero.")
        else:
            st.warning("Por favor, sube al menos un archivo.")

st.markdown("</div>", unsafe_allow_html=True)