import streamlit as st
from typing import List, Dict, Optional, Callable, Any
from chat_manager import chat_manager
from datetime import datetime
import json

class ChatInterface:
    """
    Comprehensive chat interface for Streamlit applications.
    Provides full chat management capabilities including:
    - Chat creation and selection
    - Message display and input
    - Chat deletion and renaming
    - Responsive design with custom styling
    """
    
    def __init__(self, user_id: str, collection_name: str):
        self.user_id = user_id
        self.collection_name = collection_name
        self.chat_manager = chat_manager
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables for chat management"""
        if "current_chat_id" not in st.session_state:
            st.session_state.current_chat_id = None
        
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        
        if "show_rename_dialog" not in st.session_state:
            st.session_state.show_rename_dialog = False
        
        if "rename_chat_id" not in st.session_state:
            st.session_state.rename_chat_id = None
    
    def inject_chat_styles(self):
        """Inject custom CSS styles for the chat interface"""
        st.markdown("""
        <style>
        /* Chat Interface Styles */
        .chat-container {
            background: white;
            border: 2px solid #00D400;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 212, 0, 0.1);
        }
        
        .chat-header {
            background: linear-gradient(135deg, #00D400, #00A300);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
            font-weight: bold;
        }
        
        .chat-selector {
            background: rgba(0, 212, 0, 0.05);
            border: 1px solid #00D400;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .chat-controls {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }
        
        .chat-message-user {
            background: rgba(0, 212, 0, 0.1) !important;
            border-left: 4px solid #00D400 !important;
            border-radius: 10px !important;
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
        }
        
        .chat-message-assistant {
            background: rgba(0, 0, 0, 0.05) !important;
            border-left: 4px solid #666666 !important;
            border-radius: 10px !important;
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
        }
        
        .empty-chat {
            text-align: center;
            padding: 3rem 2rem;
            background: rgba(0, 212, 0, 0.05);
            border: 2px dashed #00D400;
            border-radius: 15px;
            margin: 2rem 0;
        }
        
        .empty-chat h3 {
            color: #00D400;
            margin-bottom: 1rem;
        }
        
        .empty-chat p {
            color: #666666;
            font-size: 1.1rem;
        }
        
        .chat-stats {
            background: rgba(0, 212, 0, 0.1);
            border: 1px solid #00D400;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: #00A300;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #00D400, #00A300) !important;
            border: none !important;
            border-radius: 8px !important;
            color: white !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 10px rgba(0, 212, 0, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(0, 212, 0, 0.4) !important;
        }
        
        /* Danger button styling */
        .danger-btn button {
            background: linear-gradient(135deg, #ff4444, #cc0000) !important;
        }
        
        /* Secondary button styling */
        .secondary-btn button {
            background: rgba(0, 212, 0, 0.1) !important;
            border: 2px solid #00D400 !important;
            color: #00D400 !important;
        }
        
        /* Warning button styling */
        .warning-btn button {
            background: linear-gradient(135deg, #ffa500, #ff8c00) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _ensure_active_chat(self) -> str:
        """Ensure there's an active chat, create one if needed"""
        if not st.session_state.current_chat_id:
            # Try to load the most recent chat
            chats = self.chat_manager.list_chats(self.user_id, self.collection_name)
            if chats:
                st.session_state.current_chat_id = chats[0]["chat_id"]
                st.session_state.chat_messages = self.chat_manager.load_chat_messages(
                    self.user_id, self.collection_name, st.session_state.current_chat_id
                )
            else:
                # Create a new chat
                st.session_state.current_chat_id = self.chat_manager.create_chat(
                    self.user_id, self.collection_name, "New Conversation"
                )
                st.session_state.chat_messages = []
        
        return st.session_state.current_chat_id
    
    def render_chat_selector(self):
        """Render the chat selection and management interface"""
        st.markdown('<div class="chat-selector">', unsafe_allow_html=True)
        
        # Get available chats
        chats = self.chat_manager.list_chats(self.user_id, self.collection_name)
        
        if chats:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Create options for selectbox
                chat_options = {}
                for chat in chats:
                    title = chat["title"][:50] + ("..." if len(chat["title"]) > 50 else "")
                    updated = chat["updated_at"][:16] if chat["updated_at"] else "Unknown"
                    label = f"{title} • {updated}"
                    chat_options[label] = chat["chat_id"]
                
                # Find current selection
                current_index = 0
                if st.session_state.current_chat_id:
                    for i, (label, chat_id) in enumerate(chat_options.items()):
                        if chat_id == st.session_state.current_chat_id:
                            current_index = i
                            break
                
                selected_label = st.selectbox(
                    "Selecciona una conversación:",
                    options=list(chat_options.keys()),
                    index=current_index,
                    key="chat_selector_main"
                )
                
                # Handle chat selection change
                selected_chat_id = chat_options[selected_label]
                if selected_chat_id != st.session_state.current_chat_id:
                    st.session_state.current_chat_id = selected_chat_id
                    st.session_state.chat_messages = self.chat_manager.load_chat_messages(
                        self.user_id, self.collection_name, selected_chat_id
                    )
                    st.rerun()
            
            with col2:
                if st.button("➕ Nuevo chat", key="new_chat_btn", use_container_width=True):
                    new_chat_id = self.chat_manager.create_chat(
                        self.user_id, self.collection_name, "New Conversation"
                    )
                    st.session_state.current_chat_id = new_chat_id
                    st.session_state.chat_messages = []
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Eliminar", key="delete_chat_btn", use_container_width=True):
                    if st.session_state.current_chat_id:
                        # Show confirmation dialog
                        if st.button("⚠️ Confirmar elimminación de chat", key="confirm_delete", help="Esta acción no puede ser deshecha"):
                            self.chat_manager.delete_chat(
                                self.user_id, self.collection_name, st.session_state.current_chat_id
                            )
                            # Switch to another chat or create new one
                            remaining_chats = self.chat_manager.list_chats(self.user_id, self.collection_name)
                            if remaining_chats:
                                st.session_state.current_chat_id = remaining_chats[0]["chat_id"]
                                st.session_state.chat_messages = self.chat_manager.load_chat_messages(
                                    self.user_id, self.collection_name, st.session_state.current_chat_id
                                )
                            else:
                                st.session_state.current_chat_id = self.chat_manager.create_chat(
                                    self.user_id, self.collection_name, "New Conversation"
                                )
                                st.session_state.chat_messages = []
                            st.rerun()
            
            # Show chat statistics
            current_chat = next((c for c in chats if c["chat_id"] == st.session_state.current_chat_id), None)
            if current_chat:
                st.markdown(f"""
                <div class="chat-stats">
                    💬 {current_chat['message_count']} messages • 
                    Created: {current_chat['created_at'][:16]} • 
                    Updated: {current_chat['updated_at'][:16]}
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.info("No conversations yet. Start a new one below!")
            if st.button("🚀 Start First Conversation", key="first_chat", use_container_width=True):
                new_chat_id = self.chat_manager.create_chat(
                    self.user_id, self.collection_name, "First Conversation"
                )
                st.session_state.current_chat_id = new_chat_id
                st.session_state.chat_messages = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_chat_controls(self):
        """Render additional chat control buttons"""
        if st.session_state.current_chat_id:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Renombrar", key="rename_chat", use_container_width=True):
                    st.session_state.show_rename_dialog = True
                    st.session_state.rename_chat_id = st.session_state.current_chat_id
            
            with col2:
                if st.button("🧹 Limpiar", key="clear_chat", use_container_width=True):
                    st.session_state.chat_messages = []
                    self.chat_manager.save_chat_messages(
                        self.user_id, self.collection_name, 
                        st.session_state.current_chat_id, []
                    )
                    st.rerun()
            
            with col3:
                if st.button("📥 Exportar", key="export_chat", use_container_width=True):
                    chat_data = self.chat_manager.export_chat(
                        self.user_id, self.collection_name, st.session_state.current_chat_id
                    )
                    if chat_data:
                        st.download_button(
                            label="Descargar Chat",
                            data=json.dumps(chat_data, indent=2),
                            file_name=f"chat_{st.session_state.current_chat_id[:8]}.json",
                            mime="application/json"
                        )
            
            with col4:
                if st.button("📊 Estadísticas", key="chat_stats", use_container_width=True):
                    self._show_chat_statistics()
    
    def render_rename_dialog(self):
        """Render the chat rename dialog"""
        if st.session_state.show_rename_dialog and st.session_state.rename_chat_id:
            st.markdown("### ✏️ Renombrar conversación")
            
            # Get current title
            chat_info = self.chat_manager.get_chat_info(
                self.user_id, self.collection_name, st.session_state.rename_chat_id
            )
            current_title = chat_info["title"] if chat_info else "Untitled"
            
            new_title = st.text_input(
                "New title:",
                value=current_title,
                key="rename_input",
                max_chars=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Guardar", key="save_rename", use_container_width=True):
                    if new_title.strip():
                        success = self.chat_manager.rename_chat(
                            self.user_id, self.collection_name,
                            st.session_state.rename_chat_id, new_title.strip()
                        )
                        if success:
                            st.success("Chat renombrado correctamente!")
                            st.session_state.show_rename_dialog = False
                            st.session_state.rename_chat_id = None
                            st.rerun()
                        else:
                            st.error("Error al renombrar el chat")
                    else:
                        st.warning("Por favor, ingrese un título válido")
            
            with col2:
                if st.button("❌ Cancelar", key="cancel_rename", use_container_width=True):
                    st.session_state.show_rename_dialog = False
                    st.session_state.rename_chat_id = None
                    st.rerun()
    
    def _show_chat_statistics(self):
        """Show detailed chat statistics"""
        all_chats = self.chat_manager.list_chats(self.user_id, self.collection_name)
        total_messages = sum(chat["message_count"] for chat in all_chats)
        
        st.markdown(f"""
        ### 📊 Estadísticas de la conversación
        
        - **Conversaciones:** {len(all_chats)}
        - **Mensajes:** {total_messages}
        - **Mensajes por chat:** {total_messages / len(all_chats) if all_chats else 0:.1f}
        - **Chat más activo:** {max(all_chats, key=lambda x: x['message_count'])['title'] if all_chats else 'N/A'}
        """)
    
    def render_messages(self):
        """Render the chat messages"""
        if not st.session_state.chat_messages:
            st.markdown("""
            <div class="empty-chat">
                <h3>👋 ¡Bienvenido a tu conversación!</h3>
                <p>Haz una pregunta sobre tus documentos para empezar.</p>
                <p>Tu conversación se guardará automáticamente y podrás continuarla en cualquier momento.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    # Show additional context if available (for assistant messages)
                    if message["role"] == "assistant" and "documents" in message:
                        with st.expander("📄 View Source Documents"):
                            for i, doc in enumerate(message["documents"]):
                                # Handle both LangChain Document objects and serialized dictionaries
                                if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                                    # LangChain Document object
                                    content = doc.page_content
                                    metadata = doc.metadata
                                elif isinstance(doc, dict):
                                    # Serialized dictionary format
                                    content = doc.get('page_content', '')
                                    metadata = doc.get('metadata', {})
                                else:
                                    # Fallback
                                    content = str(doc)
                                    metadata = {}
                                
                                # Show document summary if available
                                doc_summary = metadata.get('document_summary', '')
                                if doc_summary:
                                    with st.expander(f"📋 Document Summary - {metadata.get('source_file', 'Unknown')}"):
                                        st.markdown(doc_summary)
                                
                                st.markdown(f"""
                                **Source {i+1}:** {metadata.get('source', 'Unknown')} 
                                (Page {metadata.get('page', 'N/A')})
                                
                                {content[:300]}{'...' if len(content) > 300 else ''}
                                """)
    
    def handle_user_input(self, process_message_callback: Callable[[str], Dict[str, Any]]):
        """
        Handle user input and process messages
        
        Args:
            process_message_callback: Function to process the user message and return response
                                    Should return dict with 'content' and optionally 'documents'
        """
        self._ensure_active_chat()
        
        if prompt := st.chat_input("Escribe tu mensaje aquí..."):
            # Add user message
            user_message = {"role": "user", "content": prompt}
            st.session_state.chat_messages.append(user_message)
            
            # Save immediately after user message
            self.chat_manager.save_chat_messages(
                self.user_id, self.collection_name,
                st.session_state.current_chat_id, st.session_state.chat_messages
            )
            
            # Show user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process the message and get response
            with st.spinner("Pensando..."):
                try:
                    response_data = process_message_callback(prompt)
                    
                    # Add assistant response
                    assistant_message = {
                        "role": "assistant",
                        "content": response_data.get("content", "Lo siento, no puedo procesar tu solicitud."),
                    }
                    
                    # Add documents if provided (convert to serializable format)
                    if "documents" in response_data:
                        # Convert Document objects to serializable dictionaries
                        serializable_docs = []
                        for doc in response_data["documents"]:
                            if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                                # LangChain Document object
                                serializable_docs.append({
                                    "page_content": doc.page_content,
                                    "metadata": doc.metadata
                                })
                            elif isinstance(doc, dict):
                                # Already a dictionary
                                serializable_docs.append(doc)
                            else:
                                # Fallback: convert to string
                                serializable_docs.append({
                                    "page_content": str(doc),
                                    "metadata": {}
                                })
                        assistant_message["documents"] = serializable_docs
                    
                    st.session_state.chat_messages.append(assistant_message)
                    
                    # Save after assistant response
                    self.chat_manager.save_chat_messages(
                        self.user_id, self.collection_name,
                        st.session_state.current_chat_id, st.session_state.chat_messages
                    )
                    
                    # Rerun to show the new messages
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al procesar el mensaje: {str(e)}")
    
    def render_complete_interface(self, process_message_callback: Callable[[str], Dict[str, Any]]):
        """
        Render the complete chat interface
        
        Args:
            process_message_callback: Function to process user messages
        """
        # Inject styles
        self.inject_chat_styles()
        
        # Main container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f"""
        <div class="chat-header">
            💬 Conversación con: {self.collection_name}
        </div>
        """, unsafe_allow_html=True)
        
        # Chat selector
        self.render_chat_selector()
        
        # Rename dialog (if active)
        if st.session_state.show_rename_dialog:
            self.render_rename_dialog()
        
        # Chat controls
        self.render_chat_controls()
        
        # Messages
        self.render_messages()
        
        # User input
        self.handle_user_input(process_message_callback)
        
        st.markdown('</div>', unsafe_allow_html=True) 