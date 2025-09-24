import streamlit as st
import base64
from dotenv import load_dotenv
from security import show_login, get_login_manager

load_dotenv()

def get_base64_of_image(path):
    """Convert image to base64 string"""
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def inject_css():
    """Inject custom CSS for the landing page"""
    # Get the background image as base64
    bg_image = get_base64_of_image("assets/dbd785b6bcfff2745a42f14bd492866be29dff35 (1).jpg")
    
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
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Content container */
    .main-content {{
        padding: 2rem;
        text-align: center;
        min-height: 40vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    /* Title styling */
    .main-title {{
        font-size: 3.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    }}
    
    .sub-title {{
        font-size: 1.5rem;
        color: #00D400;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }}
    
    /* Navigation buttons container */
    .nav-buttons-container {{
        margin: 1rem 0;
        padding: 0.5rem;
    }}
    
    /* Streamlit button styling */
    .stButton > button {{
        background: linear-gradient(135deg, #00D400, #00A300) !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1.5rem 2.5rem !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 15px rgba(0, 212, 0, 0.3) !important;
        height: 80px !important;
        width: 100% !important;
        text-transform: none !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 20px rgba(0, 212, 0, 0.4) !important;
        background: linear-gradient(135deg, #00F400, #00D400) !important;
        border: none !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(0, 212, 0, 0.3) !important;
    }}
    
    .stButton > button:focus {{
        outline: none !important;
        border: 2px solid #00D400 !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 0, 0.2) !important;
    }}
    
    /* User info styling */
    .user-info {{
        position: absolute;
        top: 2rem;
        right: 2rem;
        background: rgba(0, 0, 0, 0.8);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border: 2px solid #00D400;
    }}
    
    .user-name {{
        color: #00D400;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    
    
    .logout-btn:hover {{
        background: #ff6666;
        transform: scale(1.05);
    }}
    
    /* Logo styling */
    .logo {{
        font-size: 4rem;
        margin-bottom: 1rem;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .nav-buttons {{
            flex-direction: column;
            align-items: center;
        }}
        
        
        .user-info {{
            position: relative;
            top: auto;
            right: auto;
            margin-bottom: 2rem;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

st.set_page_config(
    page_title="Maxwell RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom CSS
inject_css()

# Get the login manager
login_manager = get_login_manager()

# Check if user is authenticated
if not login_manager.verify_session():
    show_login()
    st.stop()

# Get user info
name = st.session_state.get('name', '')
username = st.session_state.get('username', '')



# Main content
st.markdown("""
<div class="main-content">
    <div class="logo" style="color: white;">🤖</div>
    <h1 class="main-title" style="color: white;">Maxwell AI</h1>
    <p class="sub-title">Maximize the value of your data</p>
</div>
""", unsafe_allow_html=True)

# Main navigation buttons
st.markdown('<div class="nav-buttons-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="small")

with col1:
    if st.button("📁 Subir y procesar documentos", key="upload_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Upload_and_Process_Documents.py")

with col2:
    if st.button("💬 Conversar con los documentos", key="chat_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Chat.py")

with col3:
    if st.button("⚙️ Configuracion de sistema", key="config_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Configurations.py")

st.markdown('</div>', unsafe_allow_html=True) 