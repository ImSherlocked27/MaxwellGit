import streamlit as st
import os
from dotenv import load_dotenv, set_key, find_dotenv
from security import get_login_manager

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Configuraciones",
    page_icon="⚙️",
    layout="wide"
)

def inject_config_css():
    """Inject custom CSS for the configuration page"""
    css = """
    <style>
    /* Hide Streamlit elements */
    .stDeployButton {display:none;}
    .stDecoration {display:none;}
    #MainMenu {display:none;}
    header {display:none;}
    footer {display:none;}
    
    /* Main app container */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #333333;
        min-height: 100vh;
    }
    
    /* Page title */
    .page-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Section cards */
    .section-card {
        background: white;
        border: 2px solid #00D400;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 212, 0, 0.1);
    }
    
    .section-title {
        color: #00D400;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* API Key input styling */
    .api-key-input {
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .status-configured {
        background: rgba(0, 212, 0, 0.2);
        color: #00A300;
        border: 1px solid #00D400;
    }
    
    .status-missing {
        background: rgba(255, 68, 68, 0.2);
        color: #cc0000;
        border: 1px solid #ff4444;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D400, #00A300) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 0, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 0, 0.4) !important;
        background: linear-gradient(135deg, #00F400, #00D400) !important;
    }
    
    /* Warning button styling */
    [data-testid="stButton"]:has(button:contains("Restablecer")) button {
        background: linear-gradient(135deg, #ffa500, #ff8c00) !important;
        color: white !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_config_css()

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
    st.markdown('<h1 class="page-title">⚙️ Configuraciones del Sistema</h1>', unsafe_allow_html=True)
with col3:
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
    
    if st.button("Cerrar Sesión", key="logout_button_config", use_container_width=True):
        login_manager.logout()
        st.rerun()

# --- Helper Functions ---
def get_env_file_path():
    """Get the path to the .env file"""
    env_path = find_dotenv()
    if not env_path:
        # If .env doesn't exist, create it in the current directory
        env_path = os.path.join(os.getcwd(), '.env')
    return env_path

def save_api_key(key_name, key_value):
    """Save API key to .env file and update environment"""
    try:
        env_path = get_env_file_path()
        
        # Update the .env file
        set_key(env_path, key_name, key_value)
        
        # Update the current environment
        os.environ[key_name] = key_value
        
        return True
    except Exception as e:
        st.error(f"Error guardando {key_name}: {str(e)}")
        return False

def get_api_key_status(key_name):
    """Get the status of an API key"""
    key_value = os.environ.get(key_name, "")
    if key_value and key_value.strip():
        return "configured", key_value
    else:
        return "missing", ""

# --- Initialize session state for configurations ---
if "config" not in st.session_state:
    st.session_state.config = {
        # Model Configuration
        "gpt_model": "gpt-4o-mini",
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

config = st.session_state.config

# --- API Keys Configuration Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        🔑 Configuración de Claves API
    </div>
</div>
""", unsafe_allow_html=True)

# Get current API key statuses
openai_status, openai_key = get_api_key_status("OPENAI_API_KEY")
vision_status, vision_key = get_api_key_status("VISION_AGENT_API_KEY")

# Display current status
col1, col2 = st.columns(2)

with col1:
    st.markdown("### OpenAI API Key")
    if openai_status == "configured":
        masked_key = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else openai_key[:4] + "..."
        st.markdown(f"""
        <div>
            <strong>Estado:</strong> 
            <span class="status-indicator status-configured">✓ Configurada</span>
        </div>
        <div style="margin-top: 0.5rem;">
            <strong>Clave actual:</strong> <code>{masked_key}</code>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div>
            <strong>Estado:</strong> 
            <span class="status-indicator status-missing">✗ No configurada</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Input for new OpenAI API key
    new_openai_key = st.text_input(
        "Nueva OpenAI API Key:",
        value="",
        type="password",
        help="Introduce tu clave API de OpenAI. Se guardará en el archivo .env",
        key="openai_key_input",
        placeholder="sk-..."
    )
    
    if st.button("Guardar OpenAI API Key", key="save_openai"):
        if new_openai_key.strip():
            if save_api_key("OPENAI_API_KEY", new_openai_key.strip()):
                st.success("✅ OpenAI API Key guardada correctamente")
                st.rerun()
        else:
            st.warning("Por favor, introduce una clave API válida")

with col2:
    st.markdown("### Vision Agent API Key")
    if vision_status == "configured":
        masked_key = vision_key[:8] + "..." + vision_key[-4:] if len(vision_key) > 12 else vision_key[:4] + "..."
        st.markdown(f"""
        <div>
            <strong>Estado:</strong> 
            <span class="status-indicator status-configured">✓ Configurada</span>
        </div>
        <div style="margin-top: 0.5rem;">
            <strong>Clave actual:</strong> <code>{masked_key}</code>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div>
            <strong>Estado:</strong> 
            <span class="status-indicator status-missing">✗ No configurada</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Input for new Vision Agent API key
    new_vision_key = st.text_input(
        "Nueva Vision Agent API Key:",
        value="",
        type="password",
        help="Introduce tu clave API de Vision Agent. Se guardará en el archivo .env",
        key="vision_key_input",
        placeholder="Introduce la clave API..."
    )
    
    if st.button("Guardar Vision Agent API Key", key="save_vision"):
        if new_vision_key.strip():
            if save_api_key("VISION_AGENT_API_KEY", new_vision_key.strip()):
                st.success("✅ Vision Agent API Key guardada correctamente")
                st.rerun()
        else:
            st.warning("Por favor, introduce una clave API válida")

# Environment file info
env_path = get_env_file_path()
st.markdown(f"""
<div style="
    background: rgba(0, 212, 0, 0.1);
    border: 1px solid #00D400;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
">
    <strong>📁 Archivo de configuración:</strong> <code>{env_path}</code><br>
    <small>Las claves API se guardan en este archivo y se cargan automáticamente al iniciar la aplicación.</small>
</div>
""", unsafe_allow_html=True)

# --- Model Configuration Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        🤖 Configuración del Modelo
    </div>
</div>
""", unsafe_allow_html=True)

config["gpt_model"] = st.selectbox(
    "Selecciona Modelo GPT",
    ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"],
    index=["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"].index(config["gpt_model"])
)

config["embedding_model"] = st.selectbox(
    "Selecciona Modelo de Embeddings",
    ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"],
    index=["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"].index(config["embedding_model"])
)

config["temperature"] = st.slider("Temperatura del Modelo", 0.0, 1.0, config["temperature"], 0.05)

# --- FAISS Configuration Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        🔍 Configuración FAISS
    </div>
</div>
""", unsafe_allow_html=True)

config["retrieval_method"] = st.selectbox(
    "Selecciona Método de Recuperación",
    ["faiss_hybrid", "faiss_only", "chroma_only", "legacy_hybrid"],
    index=["faiss_hybrid", "faiss_only", "chroma_only", "legacy_hybrid"].index(config["retrieval_method"]),
    help="faiss_hybrid: FAISS + ChromaDB, faiss_only: Solo FAISS, chroma_only: Solo ChromaDB, legacy_hybrid: BM25 + ChromaDB (requiere reinstalar BM25)"
)

config["faiss_index_type"] = st.selectbox(
    "Tipo de Índice FAISS",
    ["auto", "flat", "ivf", "hnsw"],
    index=["auto", "flat", "ivf", "hnsw"].index(config["faiss_index_type"]),
    help="auto: Selección automática basada en el tamaño de la colección, flat: Búsqueda exacta, ivf: Búsqueda aproximada rápida, hnsw: Búsqueda muy rápida"
)

if config["faiss_index_type"] != "auto":
    st.info(f"Usando índice FAISS tipo: {config['faiss_index_type'].upper()}")
else:
    st.info("El tipo de índice se seleccionará automáticamente según el tamaño de la colección")

config["top_k"] = st.slider("Resultados Top-k", 1, 50, config["top_k"])

# --- System Prompt Configuration Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        💬 Configuración del Prompt del Sistema
    </div>
</div>
""", unsafe_allow_html=True)

config["system_prompt"] = st.text_area(
    "Prompt del Sistema para el Chat",
    value=config["system_prompt"],
    height=400,
    help="Este es el prompt principal que define el comportamiento del asistente Maxwell durante las conversaciones."
)

# --- Document Summarization Prompts Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        📄 Configuración de Prompts de Resumen
    </div>
</div>
""", unsafe_allow_html=True)

st.subheader("Prompt de Resumen Detallado")
config["document_summary_prompt"] = st.text_area(
    "Prompt para Resumen Detallado de Documentos",
    value=config["document_summary_prompt"],
    height=300,
    help="Este prompt se usa para crear resúmenes estructurados y detallados de los documentos procesados."
)

st.subheader("Prompt de Resumen Corto")
config["short_summary_prompt"] = st.text_area(
    "Prompt para Resumen Corto de Documentos",
    value=config["short_summary_prompt"],
    height=150,
    help="Este prompt se usa para crear resúmenes concisos de los documentos para compatibilidad."
)

# --- Save and Reset Buttons ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        💾 Guardar Configuraciones
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Guardar Configuraciones", key="save_config", use_container_width=True):
        st.session_state.config = config
        st.success("¡Configuraciones guardadas!")

with col2:
    if st.button("Restablecer Valores Predeterminados", key="reset_config", use_container_width=True):
        st.session_state.config = {
            # Model Configuration
            "gpt_model": "gpt-4o-mini",
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
        st.success("¡Configuraciones restablecidas a valores predeterminados!")
        st.rerun()

with col3:
    if st.button("🔄 Recargar desde .env", key="reload_env", use_container_width=True):
        load_dotenv(override=True)  # Reload environment variables
        st.success("¡Variables de entorno recargadas!")
        st.rerun()

# --- Information Section ---
st.markdown("""
<div class="section-card">
    <div class="section-title">
        ℹ️ Información sobre Configuraciones
    </div>
    <div style="color: #666; line-height: 1.6;">
        <h4>🔑 Claves API</h4>
        <ul>
            <li><strong>OpenAI API Key:</strong> Requerida para el modelo GPT y embeddings de OpenAI</li>
            <li><strong>Vision Agent API Key:</strong> Requerida para funcionalidades de análisis visual (OCR avanzado)</li>
        </ul>
        
        <h4>🤖 Modelos</h4>
        <ul>
            <li><strong>GPT-4o-mini:</strong> Modelo más rápido y económico (recomendado)</li>
            <li><strong>GPT-4o:</strong> Modelo más potente para tareas complejas</li>
            <li><strong>Temperatura:</strong> Controla la creatividad (0.0 = más determinista, 1.0 = más creativo)</li>
        </ul>
        
        <h4>🔍 Recuperación</h4>
        <ul>
            <li><strong>FAISS Hybrid:</strong> Combina búsqueda semántica y vectorial (recomendado)</li>
            <li><strong>Top-k:</strong> Número de documentos más relevantes a recuperar</li>
        </ul>
        
        <p><strong>Nota:</strong> Los cambios en las claves API requieren reiniciar la aplicación para tomar efecto completo.</p>
    </div>
</div>
""", unsafe_allow_html=True)