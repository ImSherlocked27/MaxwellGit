# 2_Chat.py - Enhanced with Comprehensive Chat Management System

import streamlit as st
from security import get_login_manager
import chromadb
import os
from operator import itemgetter
import json

# --- LangChain Imports for the Advanced RAG Chain ---
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from faiss_retriever import FAISSRetriever, HybridFAISSRetriever, create_faiss_retriever, get_optimal_index_type
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

# Import the new chat management system
from chat_manager import chat_manager
from chat_interface import ChatInterface

def inject_chat_css():
	"""Inject custom CSS for the chat page with enhanced styling"""
	
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
	
	/* Enhanced Chat Interface Styles */
	.chat-container {{
		background: white;
		border: 2px solid #00D400;
		border-radius: 15px;
		padding: 1.5rem;
		margin: 1rem 0;
		box-shadow: 0 8px 32px rgba(0, 212, 0, 0.1);
	}}
	
	.chat-header {{
		background: linear-gradient(135deg, #00D400, #00A300);
		color: white;
		padding: 1rem;
		border-radius: 10px;
		margin-bottom: 1rem;
		text-align: center;
		font-weight: bold;
		font-size: 1.2rem;
	}}
	
	.chat-selector {{
		background: rgba(0, 212, 0, 0.05);
		border: 1px solid #00D400;
		border-radius: 10px;
		padding: 1rem;
		margin: 1rem 0;
	}}
	
	.chat-stats {{
		background: rgba(0, 212, 0, 0.1);
		border: 1px solid #00D400;
		border-radius: 8px;
		padding: 0.5rem 1rem;
		margin: 0.5rem 0;
		font-size: 0.9rem;
		color: #00A300;
		display: flex;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
	}}
	
	.empty-chat {{
		text-align: center;
		padding: 3rem 2rem;
		background: rgba(0, 212, 0, 0.05);
		border: 2px dashed #00D400;
		border-radius: 15px;
		margin: 2rem 0;
	}}
	
	.empty-chat h3 {{
		color: #00D400;
		margin-bottom: 1rem;
		font-size: 1.5rem;
	}}
	
	.empty-chat p {{
		color: #666666;
		font-size: 1.1rem;
		margin: 0.5rem 0;
	}}
	
	/* Chat messages */
	.stChatMessage {{
		border-radius: 10px !important;
		margin: 0.5rem 0 !important;
		padding: 1rem !important;
		border: 1px solid #e0e0e0 !important;
	}}
	
	.stChatMessage[data-testid="user-message"] {{
		background: rgba(0, 212, 0, 0.1) !important;
		border-left: 4px solid #00D400 !important;
		border: 1px solid #00D400 !important;
	}}
	
	.stChatMessage[data-testid="assistant-message"] {{
		background: rgba(0, 0, 0, 0.05) !important;
		border-left: 4px solid #666666 !important;
		border: 1px solid #e0e0e0 !important;
	}}
	
	/* Chat input */
	.stChatInput > div {{
		background: white !important;
		border: 2px solid #00D400 !important;
		border-radius: 25px !important;
		box-shadow: 0 4px 15px rgba(0, 212, 0, 0.2) !important;
	}}
	
	.stChatInput input {{
		background: transparent !important;
		color: #333333 !important;
		border: none !important;
		padding: 1rem 1.5rem !important;
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
	
	/* Home button styling */
	[data-testid="stButton"]:has(button:contains("Inicio")) button {{
		background: rgba(0, 212, 0, 0.1) !important;
		border: 2px solid #00D400 !important;
		color: #00D400 !important;
	}}
	
	/* Logout button styling */
	[data-testid="stButton"]:has(button:contains("Cerrar")) button {{
		background: linear-gradient(135deg, #ff4444, #cc0000) !important;
		color: white !important;
	}}
	
	/* Delete button styling */
	[data-testid="stButton"]:has(button:contains("Delete")) button,
	[data-testid="stButton"]:has(button:contains("🗑️")) button {{
		background: linear-gradient(135deg, #ff4444, #cc0000) !important;
		color: white !important;
	}}
	
	/* Warning button styling */
	[data-testid="stButton"]:has(button:contains("Clear")) button,
	[data-testid="stButton"]:has(button:contains("🧹")) button {{
		background: linear-gradient(135deg, #ffa500, #ff8c00) !important;
		color: white !important;
	}}
	
	/* Selectbox styling */
	.stSelectbox > div > div > div {{
		background: white !important;
		border: 2px solid #00D400 !important;
		border-radius: 10px !important;
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
	
	/* Responsive design */
	@media (max-width: 768px) {{
		.section-card {{
			padding: 1rem;
			margin: 1rem 0;
		}}
		
		.page-title {{
			font-size: 2rem;
		}}
		
		.chat-stats {{
			flex-direction: column;
			align-items: flex-start;
		}}
	}}
	</style>
	"""
	st.markdown(css, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
	page_title="Conversar con documentos",
	page_icon="💬",
	layout="wide",
	initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_chat_css()

# Get the login manager
login_manager = get_login_manager()

# Check authentication status
if not login_manager.verify_session():
	st.error('Por favor, inicia sesión para acceder a esta página.')
	st.stop()

# User is authenticated - show the page content
name = st.session_state.get('name', '')

# Establish a stable user identifier for chat storage
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = (
        st.session_state.get('user_id')
        or st.session_state.get('email')
        or st.session_state.get('name')
        or "anonymous"
    )

# Navigation header
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
	if st.button("🏠 Inicio", key="home_btn", help="Volver al inicio"):
		st.switch_page("app.py")
with col2:
	st.markdown('<h1 class="page-title">💬 Conversar con Documentos</h1>', unsafe_allow_html=True)
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
		
		if st.button("Cerrar Sesión", key="logout_button_chat", use_container_width=True):
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

# --- Database Selection Section ---
st.markdown("""
<div class="section-card">
	<div class="section-title">
		🗄️ Seleccionar Base de Datos
	</div>
</div>
""", unsafe_allow_html=True)

try:
	collections = client.list_collections()
	collection_names = [c.name for c in collections]
except Exception as e:
	st.error(f"Error conectando a ChromaDB: {e}")
	collection_names = []

if not collection_names:
	st.warning("Por favor, crea una base de datos vectorial y sube documentos primero.")
	st.markdown("""
	<div style="text-align: center; margin: 2rem 0;">
		<p>📁 Ve a la página de <strong>Subir y Procesar Documentos</strong> para comenzar</p>
	</div>
	""", unsafe_allow_html=True)
	
	if st.button("📁 Ir a Subir Documentos", key="go_upload", use_container_width=True):
		st.switch_page("pages/1_Upload_and_Process_Documents.py")
	st.stop()

selected_collection = st.selectbox(
	"Selecciona la base de datos con la que quieres conversar:", 
	collection_names,
	help="Elige la base de datos que contiene los documentos con los que quieres chatear"
)

st.markdown("</div>", unsafe_allow_html=True)

# --- RAG Chain Initialization (same as before) ---
@st.cache_resource(ttl=3600) # Cache for 1 hour
def initialize_rag_chain(_collection_name: str, _chroma_fingerprint: str):
	"""Initialize the full advanced RAG chain with Hybrid Search - ChromaDB only."""
	config = st.session_state.config

	# --- 1. Initialize Embedding Model ---
	embedding_model_name = config["embedding_model"]
	use_openai_embeddings = ("openai" in embedding_model_name) or ("text-embedding" in embedding_model_name)
	if use_openai_embeddings and not os.environ.get("OPENAI_API_KEY"):
		st.error("Variable de entorno OPENAI_API_KEY no configurada.")
		st.stop()

	embeddings = (
		OpenAIEmbeddings(model=embedding_model_name)
		if use_openai_embeddings
		else HuggingFaceEmbeddings(model_name=embedding_model_name)
	)

	# --- 2. Initialize Vectorstore (Dense Retriever) ---
	vectorstore = Chroma(
		collection_name=_collection_name,
		persist_directory=CHROMA_DB_PATH,
		embedding_function=embeddings
	)

	# --- 3. Load Chunks for BM25 directly from ChromaDB ---
	try:
		# Get all documents and metadata from ChromaDB
		raw = vectorstore._collection.get(include=["documents", "metadatas"])  # type: ignore[attr-defined]
		docs_list = raw.get("documents", []) if raw else []
		metas_list = raw.get("metadatas", []) if raw else []
		
		if not docs_list:
			st.error(f"Error: No se encontraron documentos en la colección '{_collection_name}'. Por favor, vuelve a procesar los documentos.")
			return None
		
		# Reconstruct Document objects for BM25
		loaded_chunks = [
			Document(
				page_content=(doc_text or ""),
				metadata=(metas_list[i] if i < len(metas_list) else {})
			)
			for i, doc_text in enumerate(docs_list)
		]
		
		print(f"Loaded {len(loaded_chunks)} chunks from ChromaDB for collection '{_collection_name}'")
		
	except Exception as e:
		st.error(f"Error loading documents from ChromaDB: {str(e)}")
		return None

	# --- 4. Initialize Retrievers Based on Configuration ---
	retrieval_method = config.get("retrieval_method", "faiss_hybrid")
	faiss_index_type = config.get("faiss_index_type", "auto")
	
	# ChromaDB Vector-based (Dense) Retriever
	chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": config["top_k"]})
	
	# Initialize FAISS retriever if needed
	faiss_retriever = None
	if retrieval_method in ["faiss_hybrid", "faiss_only"]:
		try:
			# Determine index type
			if faiss_index_type == "auto":
				optimal_index_type = get_optimal_index_type(len(loaded_chunks))
			else:
				optimal_index_type = faiss_index_type
			
			faiss_retriever = create_faiss_retriever(
				documents=loaded_chunks,
				embeddings=embeddings,
				k=config["top_k"],
				index_type=optimal_index_type,
				collection_name=_collection_name
			)
			
			print(f"FAISS retriever initialized with {optimal_index_type} index")
			
		except ImportError as e:
			st.error("FAISS no disponible. Instala con: pip install faiss-cpu")
			st.error("Cambiando a búsqueda solo con ChromaDB.")
			retrieval_method = "chroma_only"
		except Exception as e:
			st.error(f"Error inicializando FAISS: {str(e)}")
			st.error("Cambiando a búsqueda solo con ChromaDB.")
			retrieval_method = "chroma_only"
	
	# Configure retriever based on method
	if retrieval_method == "faiss_hybrid" and faiss_retriever:
		ensemble_retriever = HybridFAISSRetriever(
			faiss_retriever=faiss_retriever,
			chroma_retriever=chroma_retriever,
			weights=[0.6, 0.4],  # Favor FAISS slightly
			k=config["top_k"]
		)
		print("Using Hybrid FAISS + ChromaDB retrieval")
	elif retrieval_method == "faiss_only" and faiss_retriever:
		ensemble_retriever = faiss_retriever
		print("Using FAISS-only retrieval")
	elif retrieval_method == "chroma_only":
		ensemble_retriever = chroma_retriever
		print("Using ChromaDB-only retrieval")
	elif retrieval_method == "legacy_hybrid":
		# Fallback to BM25 + ChromaDB (requires BM25Retriever)
		try:
			from langchain.retrievers import BM25Retriever, EnsembleRetriever
			bm25_retriever = BM25Retriever.from_documents(loaded_chunks)
			bm25_retriever.k = config["top_k"]
			ensemble_retriever = EnsembleRetriever(
				retrievers=[bm25_retriever, chroma_retriever],
				weights=[0.5, 0.5]
			)
			print("Using Legacy BM25 + ChromaDB retrieval")
		except ImportError:
			st.error("BM25Retriever no disponible. Usando ChromaDB solamente.")
			ensemble_retriever = chroma_retriever
			print("Using ChromaDB-only retrieval (BM25 not available)")
	else:
		# Default fallback
		ensemble_retriever = chroma_retriever
		print("Using ChromaDB-only retrieval (default fallback)")

	# --- 5. Initialize Re-ranker (DISABLED for faster performance) ---
	# cross_encoder_model = HuggingFaceCrossEncoder(
	# 	model_name="jinaai/jina-reranker-v2-base-multilingual",
	# 	model_kwargs={"trust_remote_code": True}
	# )
	# compressor = CrossEncoderReranker(model=cross_encoder_model, top_n=15)
	# 
	# compression_retriever = ContextualCompressionRetriever(
	# 	base_compressor=compressor,
	# 	base_retriever=ensemble_retriever
	# )
	
	# Use ensemble retriever directly (without re-ranking for faster performance)
	compression_retriever = ensemble_retriever

	# --- 6. Define the Prompt and LLM ---
	if not os.environ.get("OPENAI_API_KEY"):
		st.error("Variable de entorno OPENAI_API_KEY no configurada para el modelo de chat.")
		st.stop()

	llm = ChatOpenAI(model_name=config["gpt_model"], temperature=config["temperature"])

	# Use the configurable system prompt from session state
	prompt_template = config.get("system_prompt", """You are Maxwell, a talkative but precise financial-data assistant for an enterprise RAG system.
	Your only knowledge source is the <context> block plus the <chat_history>. Do not use outside knowledge.

	— Goals —
	1) Answer the user’s question strictly using the provided context and previous messages.
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
	• “what can you do?” → Briefly describe tasks you can perform on this dataset (e.g., list clients present in context, summarize accounts and balances, trace payments, extract contract/loan terms, find overdue invoices), and give 3–5 example queries. Do not claim capabilities unrelated to data types in context.
	• “what clients we have registered?” → Return unique client names/IDs found in context. Include any available fields (e.g., legal_name, client_id, accounts_count, invoices_count). Add a Sources section.
	• “which of them have loans?” → Return only clients with loans. For each, show key fields available (loan_id, principal, current_balance, interest_rate, status, origination_date, maturity_date). Add Sources.
	• “details about a specific document or client” → Provide the requested details (e.g., totals, balances, terms, parties, dates). If multiple matches exist, summarize each briefly. Always include Sources.

	— What NOT to do —
	- Don’t answer with knowledge not supported by context.
	- Don’t guess unknown fields; write “not found in provided data”.
	- Don’t expose chain-of-thought; give conclusions and the minimal reasoning needed.

	— If context is missing/empty —
	Say you can’t answer from the provided data and ask for the exact thing needed (file name, date range, client ID, document type).

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
	3) End with a “Sources” section listing filenames/ids and, if available, page/section references used.
	4) If the answer is partial or blocked by missing data, state that explicitly and ask for the minimal follow-up needed.""")

	prompt = ChatPromptTemplate.from_template(prompt_template)

	def format_docs(docs):
		return "\n\n".join(f"Fuente: {doc.metadata.get('source', 'N/A')}, Página: {doc.metadata.get('page', 'N/A')}\nContenido: {doc.page_content}" for doc in docs)

	def _format_chat_history(chat_history):
		return "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)

	# --- 7. Build the LCEL Chain ---
	rag_chain = (
		RunnablePassthrough.assign(
			context=itemgetter("question") | compression_retriever | format_docs
		)
		| RunnablePassthrough.assign(
			chat_history=lambda x: _format_chat_history(x["chat_history"])
		)
		| RunnableParallel(
			answer=(prompt | llm | StrOutputParser()),
			documents=itemgetter("question") | compression_retriever
		)
	)
	return rag_chain

# --- Enhanced Chat Interface with New Management System ---
if selected_collection:
	# Initialize RAG chain if needed
	current_user_id = st.session_state.current_user_id
	if (
		"rag_chain" not in st.session_state
		or st.session_state.get("selected_collection") != selected_collection
		or st.session_state.get("rag_chain") is None
	):
		with st.spinner("Inicializando motor de conversación avanzado..."):
			# Create a simple fingerprint based on collection name for caching
			chroma_fingerprint = f"{selected_collection}_chromadb"
			st.session_state.rag_chain = initialize_rag_chain(selected_collection, chroma_fingerprint)
			st.session_state.selected_collection = selected_collection

	# Initialize the enhanced chat interface
	chat_interface = ChatInterface(current_user_id, selected_collection)
	
	# Configuration button
	col_config, col_empty = st.columns([1, 4])
	with col_config:
		if st.button("⚙️ Configuración", key="go_config", use_container_width=True):
			st.switch_page("pages/3_Configurations.py")

	# Define the message processing function
	def process_user_message(user_message: str) -> dict:
		"""Process user message through the RAG chain and return response with documents."""
		try:
			if st.session_state.rag_chain:
				# Get current chat messages for context
				current_messages = st.session_state.get('chat_messages', [])
				
				# Prepare chat history (exclude the current question)
				chat_history = current_messages[:-1] if current_messages else []
				
				# Invoke the RAG chain
				result = st.session_state.rag_chain.invoke({
					"question": user_message,
					"chat_history": chat_history
				})
				
				return {
					"content": result["answer"],
					"documents": result.get("documents", [])
				}
			else:
				return {
					"content": "Lo siento, el motor de conversación no está inicializado. Por favor, revisa la selección de la base de datos.",
					"documents": []
				}
		except Exception as e:
			return {
				"content": f"Ocurrió un error al procesar tu mensaje: {str(e)}",
				"documents": []
			}

	# Render the complete enhanced chat interface
	chat_interface.render_complete_interface(process_user_message)

else:
	st.warning("Por favor, selecciona una base de datos para comenzar a chatear.") 