"""
Módulo de autenticación para Maxwell AI usando streamlit-authenticator.
Implementa autenticación segura con bloqueo de IP y rate limiting.
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time
import logging
import bcrypt
from pathlib import Path
from typing import Dict, Optional, Tuple
import uuid
import sys
import locale

# Configurar encoding UTF-8 para el sistema
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

# Configurar locale para manejar caracteres especiales
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# Configurar directorio de logs
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'auth.log'

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('maxwell_auth')

def init_security_session_state():
    """Inicializa las variables de estado de la sesión para seguridad."""
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = {}
    if 'blocked_ips' not in st.session_state:
        st.session_state.blocked_ips = {}
    if 'rate_limits' not in st.session_state:
        st.session_state.rate_limits = {}
    if 'auth_key' not in st.session_state:
        st.session_state.auth_key = str(uuid.uuid4())
    if 'login_manager_initialized' not in st.session_state:
        st.session_state.login_manager_initialized = True

class LoginManager:
    """Gestor de autenticación y seguridad."""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa patrón singleton para evitar múltiples instancias."""
        if cls._instance is None:
            cls._instance = super(LoginManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor solo una vez."""
        # Asegurar que el estado de la sesión esté inicializado
        init_security_session_state()
        
        if not self._initialized:
            self.config_path = Path(__file__).parent / 'config.yaml'
            self._load_config()
            LoginManager._initialized = True
        
    def _load_config(self):
        """Carga la configuración desde el archivo YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.load(file, Loader=SafeLoader)
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
        
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica si la contraseña coincide con el hash."""
        try:
            # Asegurar que tanto la contraseña como el hash están en UTF-8
            if isinstance(password, str):
                password_bytes = password.encode('utf-8')
            else:
                password_bytes = password
                
            if isinstance(hashed, str):
                hashed_bytes = hashed.encode('utf-8')
            else:
                hashed_bytes = hashed
                
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
        
    def _check_rate_limit(self, ip: str) -> bool:
        """Verifica si una IP ha excedido el límite de solicitudes."""
        # Asegurar inicialización
        init_security_session_state()
        
        now = time.time()
        if ip not in st.session_state.rate_limits:
            st.session_state.rate_limits[ip] = {'count': 0, 'window_start': now}
            
        window = st.session_state.rate_limits[ip]
        window_duration = self.config['security']['rate_limit_window_hours'] * 3600
        
        if now - window['window_start'] > window_duration:
            window['count'] = 0
            window['window_start'] = now
            
        window['count'] += 1
        return window['count'] <= self.config['security']['max_requests_per_window']
        
    def _is_ip_blocked(self, ip: str) -> Tuple[bool, Optional[int]]:
        """Verifica si una IP está bloqueada y retorna el tiempo restante."""
        # Asegurar inicialización
        init_security_session_state()
        
        if ip in st.session_state.blocked_ips:
            block_until = st.session_state.blocked_ips[ip]
            if time.time() < block_until:
                return True, int(block_until - time.time())
            del st.session_state.blocked_ips[ip]
        return False, None
        
    def _block_ip(self, ip: str):
        """Bloquea una IP por el tiempo configurado."""
        # Asegurar inicialización
        init_security_session_state()
        
        block_duration = self.config['security']['block_duration_minutes'] * 60
        st.session_state.blocked_ips[ip] = time.time() + block_duration
        logger.warning(f"IP bloqueada: {ip}")
        
    def login_with_credentials(self, username_or_email: str, password: str, ip: str) -> Tuple[bool, str]:
        """Intenta iniciar sesión con credenciales manuales."""
        try:
            # Asegurar inicialización
            init_security_session_state()
            
            # Verificar rate limit
            if not self._check_rate_limit(ip):
                logger.warning(f"Rate limit excedido para IP: {ip}")
                return False, "Demasiadas solicitudes. Por favor, intente más tarde."
                
            # Verificar si la IP está bloqueada
            is_blocked, remaining = self._is_ip_blocked(ip)
            if is_blocked:
                return False, f"IP bloqueada. Intente de nuevo en {remaining} segundos."
                
            # Buscar usuario por nombre de usuario o email
            user_found = None
            # Asegurar que el input esté en UTF-8
            username_or_email = ensure_utf8_string(username_or_email)
            
            for username, user_data in self.config['credentials']['usernames'].items():
                # Asegurar que los datos del usuario estén en UTF-8
                user_username = ensure_utf8_string(username)
                user_email = ensure_utf8_string(user_data['email'])
                
                if user_username == username_or_email or user_email == username_or_email:
                    user_found = (username, user_data)
                    break
                    
            if user_found:
                username, user_data = user_found
                stored_password = user_data['password']
                if self._verify_password(password, stored_password):
                    # Login exitoso
                    st.session_state.authentication_status = True
                    st.session_state.username = username
                    # Asegurar que el nombre se maneja correctamente con UTF-8
                    user_name = ensure_utf8_string(user_data['name'])
                    st.session_state.name = user_name
                    # Limpiar intentos de login para esta IP
                    if ip in st.session_state.login_attempts:
                        del st.session_state.login_attempts[ip]
                    logger.info(f"Login exitoso para usuario: {username}")
                    return True, f"¡Bienvenido {user_name}!"
                    
            # Login fallido
            if ip not in st.session_state.login_attempts:
                st.session_state.login_attempts[ip] = 0
            st.session_state.login_attempts[ip] += 1
            
            if st.session_state.login_attempts[ip] >= self.config['security']['max_login_attempts']:
                self._block_ip(ip)
                return False, f"Demasiados intentos fallidos. IP bloqueada por {self.config['security']['block_duration_minutes']} minutos."
                
            remaining_attempts = self.config['security']['max_login_attempts'] - st.session_state.login_attempts[ip]
            return False, f"Credenciales incorrectas. Intentos restantes: {remaining_attempts}"
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False, "Error interno del servidor"
            
    def logout(self):
        """Cierra la sesión del usuario."""
        try:
            username = st.session_state.get('username')
            # Limpiar estado de sesión de autenticación
            keys_to_clear = ['authentication_status', 'username', 'name']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            logger.info(f"Sesión cerrada para usuario: {username}")
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            
    def verify_session(self) -> bool:
        """Verifica si la sesión actual es válida."""
        try:
            return st.session_state.get('authentication_status', False)
        except Exception as e:
            logger.error(f"Error verificando sesión: {e}")
            return False

def get_login_manager():
    """Función para obtener la instancia singleton del LoginManager."""
    # Asegurar que el estado de la sesión esté inicializado antes de crear la instancia
    init_security_session_state()
    
    if 'login_manager_instance' not in st.session_state:
        st.session_state.login_manager_instance = LoginManager()
    return st.session_state.login_manager_instance

def ensure_utf8_string(text):
    """Asegura que una cadena esté correctamente codificada en UTF-8."""
    if text is None:
        return ""
    
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return text.decode('latin-1')
            except UnicodeDecodeError:
                return text.decode('utf-8', errors='replace')
    
    if isinstance(text, str):
        # Si ya es string, asegurar que está correctamente codificado
        try:
            # Intentar recodificar para detectar problemas
            text.encode('utf-8')
            return text
        except UnicodeEncodeError:
            return text.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
    
    return str(text)

def configure_streamlit_encoding():
    """Configura Streamlit para manejar correctamente UTF-8."""
    # Configurar el encoding de la página
    st.markdown("""
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    """, unsafe_allow_html=True)

def show_login():
    """Muestra la interfaz de login personalizada."""
    # Configurar encoding antes de cualquier operación
    configure_streamlit_encoding()
    
    # Asegurar inicialización antes de cualquier operación
    init_security_session_state()
    
    # Usar la función getter para obtener la instancia
    login_manager = get_login_manager()
    
    # Obtener IP del cliente (en producción usar request.headers.get('X-Forwarded-For'))
    client_ip = "127.0.0.1"  # En producción, obtener la IP real
    
    # Estilos CSS personalizados con tema verde
    st.markdown("""
        <style>
        /* Estilo principal del contenedor de login */
        .login-container {
            max-width: 500px;
            margin: 40px auto;
            padding: 50px 40px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 212, 0, 0.2);
            background: linear-gradient(135deg, #00D400 0%, #00A000 50%, #007000 100%);
            border: 2px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }
        
        /* Efecto de brillo en el contenedor */
        .login-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Título principal */
        .login-title {
            text-align: center;
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 10px;
            color: white !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5) !important;
            letter-spacing: 2px;
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Subtítulo */
        .login-subtitle {
            text-align: center;
            font-size: 1.3em;
            margin-bottom: 40px;
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 300;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        /* Etiquetas de los campos */
        .stTextInput > label {
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.1em !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3) !important;
            margin-bottom: 8px !important;
        }
        
        /* Campos de entrada */
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            font-size: 16px !important;
            color: #333 !important;
            font-weight: 500 !important;
            box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #00FF00 !important;
            box-shadow: 0 0 0 3px rgba(0, 255, 0, 0.2), inset 0 2px 6px rgba(0, 0, 0, 0.1) !important;
            background-color: white !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #888 !important;
            font-style: italic !important;
        }
        
        /* Botones */
        .stButton > button {
            background: linear-gradient(45deg, #00FF00 0%, #00D400 50%, #00A000 100%) !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 16px 24px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 4px 15px rgba(0, 212, 0, 0.3) !important;
            text-shadow: none !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 212, 0, 0.4) !important;
            background: linear-gradient(45deg, #00FF00 0%, #00E600 50%, #00B000 100%) !important;
            color: #000000 !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
            color: #000000 !important;
        }
        
        /* Asegurar que el texto del botón sea visible */
        div[data-testid="stForm"] .stButton > button {
            color: #000000 !important;
            background: linear-gradient(45deg, #00FF00 0%, #00D400 50%, #00A000 100%) !important;
        }
        
        div[data-testid="stForm"] .stButton > button:hover {
            color: #000000 !important;
        }
        
        /* Expandir información de seguridad */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        .streamlit-expanderContent {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 0 0 10px 10px !important;
            color: white !important;
        }
        
        /* Mensajes de error y éxito */
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Ocultar elementos innecesarios */
        .stDeployButton {
            display: none !important;
        }
        
        /* Fondo general de la página */
        .stApp {
            background: linear-gradient(135deg, #001100 0%, #002200 50%, #003300 100%);
        }
        
        /* Contenedor principal */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Verificar si la IP está bloqueada
    is_blocked, remaining = login_manager._is_ip_blocked(client_ip)
    if is_blocked:
        st.error(f"🚫 IP bloqueada. Intente de nuevo en {remaining} segundos.")
        st.stop()
    
    with st.container():
        #st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Título con diseño mejorado
        st.markdown('<h1 class="login-title">🤖 Maxwell AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">🔒 Acceso Seguro al Sistema</p>', unsafe_allow_html=True)
        
        # Formulario de login
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Usuario o Email",
                placeholder="Ingrese su usuario o dirección de email",
                key="login_username",
                help="Puede usar su nombre de usuario o dirección de email"
            )
            password = st.text_input(
                "🔑 Contraseña",
                type="password",
                placeholder="Ingrese su contraseña segura",
                key="login_password",
                help="Contraseña de acceso al sistema"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Single centered login button
            submitted = st.form_submit_button("🚀 [Iniciar Sesión]")
            
            if submitted:
                if not username or not password:
                    st.error("⚠️ Por favor, complete todos los campos obligatorios")
                else:
                    success, message = login_manager.login_with_credentials(username, password, client_ip)
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
        st.markdown('</div>', unsafe_allow_html=True)
