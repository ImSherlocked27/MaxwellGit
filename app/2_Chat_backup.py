# 2_Chat.py

import streamlit as st
from security import get_login_manager
import chromadb
import os
from operator import itemgetter

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
from chat_storage import (
    load_chat_history,
    save_chat_history,
    delete_chat_history,
    list_chats,
    create_chat,
    load_chat_messages,
    save_chat_messages,
    rename_chat,
    delete_chat_by_id,
)

def inject_chat_css():
	"""Inject custom CSS for the chat page"""
	
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
	
	/* Chat messages container */
	.stContainer {{
		background: transparent;
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
	
	/* Chat message text */
	.stChatMessage .stMarkdown {{
		color: #333333 !important;
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
	
	.stChatInput input::placeholder {{
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
	
	/* Clear chat button styling */
	[data-testid="stButton"]:has(button:contains("Limpiar")) button {{
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
	
	.stSelectbox > div > div > div > div {{
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
	
	/* Text color adjustments */
	.stMarkdown, .stText, p, div, span {{
		color: #333333 !important;
	}}
	
	/* User info styling */
	.user-info {{
		color: #00D400;
		font-weight: bold;
	}}
	
	/* Database selection card */
	.db-selection {{
		background: rgba(0, 212, 0, 0.05);
		border: 2px solid #00D400;
		border-radius: 10px;
		padding: 1rem;
		margin: 1rem 0;
		text-align: center;
	}}
	
	/* Chat header */
	.chat-header {{
		background: rgba(0, 212, 0, 0.1);
		border: 1px solid #00D400;
		border-radius: 10px;
		padding: 1rem;
		margin: 1rem 0;
		text-align: center;
		font-weight: bold;
		color: #00D400;
	}}
	
	/* Spinner styling */
	.stSpinner > div {{
		border-top-color: #00D400 !important;
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
		
		.stChatMessage {{
			padding: 0.75rem !important;
			margin: 0.25rem 0 !important;
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
		"gpt_model": "gpt-4o-mini",
		"embedding_model": "text-embedding-3-large",
		"retrieval_method": "hybrid",
		"chunk_size": 2000,
		"chunk_overlap": 500,
		"top_k": 15,
		"temperature": 0.7
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

# --- NEW: Advanced RAG Chain Initialization ---
@st.cache_resource(ttl=3600) # Cache for 1 hour
def initialize_rag_chain(_collection_name: str, _chroma_fingerprint: str):
	"""
	Initializes the full advanced RAG chain with Hybrid Search and Re-ranking.
	The function is cached to avoid re-initializing models on every run.
	The underscore in _collection_name tells Streamlit to hash the value, not the object itself.
	"""
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

	# --- 4. Initialize Retrievers (FAISS-based Vector Search) ---
	# a) FAISS-based Vector Retriever (replaces BM25)
	try:
		# Get optimal index type based on collection size
		optimal_index_type = get_optimal_index_type(len(loaded_chunks))
		
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
		st.error("Usando solo ChromaDB para búsqueda vectorial.")
		# Fallback to ChromaDB only
		faiss_retriever = None

	# b) ChromaDB Vector-based (Dense) Retriever
	chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": config["top_k"]})

	# c) Hybrid FAISS + ChromaDB Retriever (replaces Ensemble)
	if faiss_retriever:
		ensemble_retriever = HybridFAISSRetriever(
			faiss_retriever=faiss_retriever,
			chroma_retriever=chroma_retriever,
			weights=[0.6, 0.4],  # Favor FAISS slightly
			k=config["top_k"]
		)
		print("Using Hybrid FAISS + ChromaDB retrieval")
	else:
		# Fallback to ChromaDB only if FAISS is not available
		ensemble_retriever = chroma_retriever
		print("Using ChromaDB-only retrieval (FAISS not available)")

	# --- 5. Initialize Re-ranker ---
	cross_encoder_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
	compressor = CrossEncoderReranker(model=cross_encoder_model, top_n=15)

	compression_retriever = ContextualCompressionRetriever(
		base_compressor=compressor,
		base_retriever=ensemble_retriever
	)

	# --- 6. Define the Prompt and LLM ---
	if not os.environ.get("OPENAI_API_KEY"):
		st.error("Variable de entorno OPENAI_API_KEY no configurada para el modelo de chat.")
		st.stop()

	llm = ChatOpenAI(model_name=config["gpt_model"], temperature=config["temperature"])

	prompt_template = """
	Responde la pregunta basándote únicamente en el siguiente contexto y el historial de chat.
	Sé conciso y directo. Si no sabes la respuesta, di que no puedes encontrar la información en los documentos.
	Cita la fuente del documento (`source`) y el número de página (`page`) para cada pieza de información que utilices.
	
	Historial de Chat:
	{chat_history}
	
	Contexto:
	{context}
	
	Pregunta: {question}
	
	Respuesta:
	"""
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

# --- Chat Interface ---
if selected_collection:
	st.markdown(f"""
	<div class="chat-header">
		🤖 Conversando con: <strong>{selected_collection}</strong>
	</div>
	""", unsafe_allow_html=True)
	
	# Initialize chat state
	if "messages" not in st.session_state:
		st.session_state.messages = []
	if "active_chat_id" not in st.session_state:
		st.session_state.active_chat_id = None
	
	# LOAD history for this user+collection when collection changes or first load
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
			# Load newest chat or fallback to legacy single-chat; try alternate user identifiers if needed
			available = list_chats(current_user_id, selected_collection)
			if not available:
				# Try alternate identifiers that might have been used previously
				candidate_ids = []
				for key in ('name', 'email', 'user_id'):
					val = st.session_state.get(key)
					if val and val not in candidate_ids:
						candidate_ids.append(val)
				for cand in candidate_ids:
					if cand == current_user_id:
						continue
					cand_chats = list_chats(cand, selected_collection)
					if cand_chats:
						st.session_state.current_user_id = cand
						current_user_id = cand
						available = cand_chats
						break
					# Also try legacy single-chat for this candidate
					legacy_cand = load_chat_history(cand, selected_collection)
					if legacy_cand:
						st.session_state.current_user_id = cand
						current_user_id = cand
						st.session_state.active_chat_id = create_chat(current_user_id, selected_collection, title="Migrado")
						save_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id, legacy_cand)
						st.session_state.messages = legacy_cand
						available = list_chats(current_user_id, selected_collection)
						break
			if available:
				st.session_state.active_chat_id = available[0]["chat_id"]
				st.session_state.messages = load_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id)
			else:
				legacy = load_chat_history(current_user_id, selected_collection)
				if legacy:
					st.session_state.active_chat_id = create_chat(current_user_id, selected_collection, title="Migrado")
					save_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id, legacy)
					st.session_state.messages = legacy
				else:
					st.session_state.active_chat_id = create_chat(current_user_id, selected_collection, title="Nuevo chat")
					st.session_state.messages = []

	# Chat controls
	col1, col2, col3 = st.columns([2, 1, 1])
	with col2:
		if st.button("🗑️ Limpiar Chat", key="clear_chat", use_container_width=True):
			st.session_state.messages = []
			if st.session_state.active_chat_id:
				save_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id, [])
			st.rerun()
	
	with col3:
		if st.button("⚙️ Configuración", key="go_config", use_container_width=True):
			st.switch_page("pages/3_Configurations.py")

	# --- Chat selector (multi-chat) ---
	with st.container():
		left, mid, right = st.columns([3, 1, 1])
		with left:
			# Resolve user identifier that actually has chats for this collection
			candidate_ids = []
			for key in ("current_user_id", "user_id", "email", "name"):
				val = st.session_state.get(key)
				if val and val not in candidate_ids:
					candidate_ids.append(val)
			resolved_user_id = current_user_id
			for cand in candidate_ids:
				if list_chats(cand, selected_collection):
					resolved_user_id = cand
					break
			if resolved_user_id != current_user_id:
				st.session_state.current_user_id = resolved_user_id
				current_user_id = resolved_user_id
			chats_meta = list_chats(current_user_id, selected_collection)
			options = {f"{c['title']} ({c['updated_at']})": c["chat_id"] for c in chats_meta} if chats_meta else {}
			selected_label = None
			if options:
				# Preselect current
				for label, cid in options.items():
					if cid == st.session_state.active_chat_id:
						selected_label = label
						break
				new_label = st.selectbox(
					"Selecciona una conversación:",
					options=list(options.keys()),
					index=(list(options.keys()).index(selected_label) if selected_label in options else 0),
					key="chat_selector"
				)
				chosen_chat_id = options[new_label]
				if chosen_chat_id != st.session_state.active_chat_id:
					st.session_state.active_chat_id = chosen_chat_id
					st.session_state.messages = load_chat_messages(current_user_id, selected_collection, chosen_chat_id)
					st.rerun()
			else:
				st.info("No hay conversaciones aún para esta base de datos.")
		with mid:
			if st.button("➕ Nuevo chat", key="new_chat_btn", use_container_width=True):
				new_id = create_chat(current_user_id, selected_collection, title="Nuevo chat")
				st.session_state.active_chat_id = new_id
				st.session_state.messages = []
				st.rerun()
		with right:
			if st.button("🗑️ Borrar chat", key="delete_chat_btn", use_container_width=True):
				if st.session_state.active_chat_id:
					delete_chat_by_id(current_user_id, selected_collection, st.session_state.active_chat_id)
					# Select next available chat or create one
					remaining = list_chats(current_user_id, selected_collection)
					if remaining:
						st.session_state.active_chat_id = remaining[0]["chat_id"]
						st.session_state.messages = load_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id)
					else:
						st.session_state.active_chat_id = create_chat(current_user_id, selected_collection, title="Nuevo chat")
						st.session_state.messages = []
					st.rerun()

	# Chat messages section
	st.markdown("""
	<div class="section-card">
		<div class="section-title">
			💬 Conversación
		</div>
	</div>
	""", unsafe_allow_html=True)
	
	chat_container = st.container()
	with chat_container:
		if not st.session_state.messages:
			st.markdown("""
			<div style="text-align: center; padding: 2rem; color: #888888; background: rgba(0, 212, 0, 0.05); border-radius: 10px; margin: 1rem 0;">
				<h3>👋 ¡Hola! ¿En qué puedo ayudarte?</h3>
				<p>Haz cualquier pregunta sobre los documentos en tu base de datos.</p>
			</div>
			""", unsafe_allow_html=True)
		
		for message in st.session_state.messages:
			with st.chat_message(message["role"]):
				st.markdown(message["content"])
				# NEW: Display the source documents in an expander
				if message["role"] == "assistant" and "documents" in message:
					with st.expander("Ver Contexto Utilizado"):
						for doc in message["documents"]:
							st.info(f"""
							**Fuente:** {doc.metadata.get('source', 'N/A')} | **Página:** {doc.metadata.get('page', 'N/A')}
							
							**Resumen del Fragmento:** {doc.metadata.get('summary', 'No disponible.')}
							
							**Contenido:**\n{doc.page_content}
							""")
	
	st.markdown("</div>", unsafe_allow_html=True)

	# Chat input
	if prompt := st.chat_input("Escribe tu pregunta sobre los documentos..."):
		st.session_state.messages.append({"role": "user", "content": prompt})
		# Persist after user message
		if st.session_state.active_chat_id:
			save_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id, st.session_state.messages)
		
		with st.chat_message("user"):
			st.markdown(prompt)

		with st.spinner("Buscando en documentos, re-clasificando y pensando..."):
			try:
				if st.session_state.rag_chain:
					result = st.session_state.rag_chain.invoke({
						"question": prompt,
						"chat_history": st.session_state.messages[:-1] # Exclude the current question
					})
					
					response = result["answer"]
					retrieved_docs = result["documents"]
					
					# Add response to history with documents for transparency
					st.session_state.messages.append({
						"role": "assistant", 
						"content": response, 
						"documents": retrieved_docs
					})
					# Persist after assistant message
					if st.session_state.active_chat_id:
						save_chat_messages(current_user_id, selected_collection, st.session_state.active_chat_id, st.session_state.messages)
					st.rerun() # Rerun to display the new messages and expander
				else:
					st.error("El motor de conversación no está inicializado. Por favor, revisa la selección de la base de datos.")

			except Exception as e:
				st.error(f"Ocurrió un error: {e}")
				
else:
	st.warning("Por favor, selecciona una base de datos para comenzar a chatear.")