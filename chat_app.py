"""
PPT Generator - Chat Interface
Interfaz CIS para generar presentaciones via n8n
"""
import streamlit as st
import requests
import json

# Configuración
N8N_BASE_URL = "https://cis-ai-n8n.app.n8n.cloud"
WEBHOOK_INIT = f"{N8N_BASE_URL}/webhook/ppt-init"
WEBHOOK_CHAT = f"{N8N_BASE_URL}/webhook/ppt-chat"

# Colores CIS
CIS = {
    "rojo": "#F20034",
    "negro": "#111111",
    "blanco": "#FFFFFF",
    "gris_osc": "#1F2937",
    "turquesa": "#005670",
    "celeste": "#9BB3BC",
    "fondo": "#0E1117",
}

# Configuración de página
st.set_page_config(
    page_title="CIS • Generador de PPT",
    page_icon="📊",
    layout="wide"
)

# ===== Autenticación simple =====
def check_password():
    """Retorna True si el usuario ingresó la clave correcta."""

    # Clave desde secrets o default para desarrollo
    correct_password = st.secrets.get("password", "cis2024")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Mostrar formulario de login
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 2rem;
                background: #1F2937; border-radius: 12px; border: 2px solid #005670;">
        <h2 style="color: white; text-align: center; margin-bottom: 1rem;">🔐 Acceso CIS</h2>
        <p style="color: #9BB3BC; text-align: center;">Ingresa la clave para continuar</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Clave", type="password", key="password_input")
        if st.button("Ingresar", use_container_width=True):
            if password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Clave incorrecta")

    return False

# Verificar autenticación antes de mostrar la app
if not check_password():
    st.stop()

# ===== App principal (solo si está autenticado) =====

# Estilos CSS con paleta CIS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: {CIS["fondo"]};
    }}

    .stApp {{
        background: {CIS["fondo"]};
    }}

    .main .block-container {{
        max-width: 1200px;
        padding: 2rem 3rem;
    }}

    /* Header */
    .cis-header {{
        background: linear-gradient(135deg, {CIS["turquesa"]} 0%, #007A94 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }}
    .cis-header h1 {{
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .cis-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: #1a1d24 !important;
        border-right: 2px solid {CIS["turquesa"]} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {CIS["blanco"]} !important;
    }}

    /* Botones */
    .stButton > button {{
        background: linear-gradient(135deg, {CIS["rojo"]} 0%, #C70028 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(242, 0, 52, 0.4) !important;
    }}

    /* Success box */
    .success-box {{
        background: rgba(0, 86, 112, 0.2);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid {CIS["turquesa"]};
        margin: 1rem 0;
    }}
    .success-box strong {{
        color: #00D4FF !important;
    }}
    .success-box a {{
        color: {CIS["blanco"]} !important;
        background: {CIS["turquesa"]} !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        text-decoration: none !important;
        display: inline-block !important;
        margin-top: 0.5rem !important;
        font-weight: 600 !important;
    }}
    .success-box a:hover {{
        background: #003D4D !important;
    }}

    /* Chat messages - forzar colores para todos los temas */
    .stChatMessage {{
        background: {CIS["gris_osc"]} !important;
        border-radius: 10px !important;
    }}
    .stChatMessage div[data-testid="stMarkdownContainer"] {{
        color: {CIS["blanco"]} !important;
    }}
    .stChatMessage div[data-testid="stMarkdownContainer"] p,
    .stChatMessage div[data-testid="stMarkdownContainer"] li,
    .stChatMessage div[data-testid="stMarkdownContainer"] span,
    .stChatMessage div[data-testid="stMarkdownContainer"] strong {{
        color: {CIS["blanco"]} !important;
    }}
    .stChatMessage div[data-testid="stMarkdownContainer"] strong {{
        color: #00D4FF !important;
    }}

    /* Forzar tema oscuro global */
    .stApp, .main, [data-testid="stAppViewContainer"] {{
        background-color: {CIS["fondo"]} !important;
        color: {CIS["blanco"]} !important;
    }}

    /* Input del chat */
    .stChatInput textarea {{
        background: {CIS["gris_osc"]} !important;
        color: {CIS["blanco"]} !important;
        border: 1px solid #374151 !important;
    }}
    .stChatInput textarea::placeholder {{
        color: #9CA3AF !important;
    }}

    /* Info boxes */
    .welcome-box {{
        background: rgba(0, 86, 112, 0.15);
        border: 2px solid {CIS["turquesa"]};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    .welcome-box h3 {{
        color: {CIS["blanco"]} !important;
        margin-top: 0;
    }}
    .welcome-box p, .welcome-box li {{
        color: #E5E7EB !important;
    }}

    /* Footer */
    .cis-footer {{
        text-align: center;
        padding: 1rem;
        color: {CIS["celeste"]};
        font-size: 0.9rem;
    }}
</style>
""", unsafe_allow_html=True)

# Inicializar estado
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "presentation_id" not in st.session_state:
    st.session_state.presentation_id = None
if "presentation_url" not in st.session_state:
    st.session_state.presentation_url = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "structure" not in st.session_state:
    st.session_state.structure = None


def init_session():
    """Inicializa una nueva sesión con n8n"""
    try:
        with st.spinner("Preparando template... (copiando y extrayendo estructura)"):
            response = requests.post(WEBHOOK_INIT, json={}, timeout=60)

            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data.get("sessionId")
                st.session_state.presentation_id = data.get("presentationId")
                st.session_state.presentation_url = data.get("presentationUrl")
                st.session_state.structure = data.get("structure")
                st.session_state.initialized = True
                st.session_state.chat_history = []

                # Mensaje inicial del bot
                placeholders = data.get("structure", {}).get("uniquePlaceholders", [])
                welcome_msg = f"""¡Hola! He preparado tu presentación.

**Encontré {len(placeholders)} campos a completar.**

Cuéntame sobre tu presentación: ¿De qué trata? ¿Para qué cliente es?
Conversaremos para definir el contenido, y cuando estés listo, dime "generar" para crear la PPT."""

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": welcome_msg
                })
                return True
            else:
                st.error(f"Error al inicializar: {response.status_code}")
                return False
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return False


def send_message(message: str):
    """Envía un mensaje al chat de n8n"""
    try:
        response = requests.post(
            WEBHOOK_CHAT,
            json={
                "sessionId": st.session_state.session_id,
                "presentationId": st.session_state.presentation_id,
                "message": message
            },
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"type": "error", "content": f"Error: {response.status_code}"}
    except Exception as e:
        return {"type": "error", "content": f"Error de conexión: {str(e)}"}


def reset_session():
    """Reinicia la sesión"""
    st.session_state.session_id = None
    st.session_state.presentation_id = None
    st.session_state.presentation_url = None
    st.session_state.chat_history = []
    st.session_state.initialized = False
    st.session_state.structure = None


# ===== UI Principal =====

# Header CIS
st.markdown("""
<div class="cis-header">
    <h1>📊 Generador de Presentaciones</h1>
    <p>Crea presentaciones personalizadas con IA</p>
</div>
""", unsafe_allow_html=True)

# Sidebar con info
with st.sidebar:
    st.markdown("### ⚙️ Sesión")

    if st.session_state.initialized:
        st.success("✓ Sesión activa")

        if st.session_state.presentation_url:
            st.markdown(f"[Ver presentación]({st.session_state.presentation_url})")

        # Mostrar estructura si existe
        if st.session_state.structure:
            with st.expander("📑 Estructura del template"):
                placeholders = st.session_state.structure.get("uniquePlaceholders", [])
                st.write(f"**{len(placeholders)} campos:**")
                for p in placeholders[:20]:  # Mostrar primeros 20
                    st.write(f"• {p}")
                if len(placeholders) > 20:
                    st.write(f"... y {len(placeholders) - 20} más")

        if st.button("🔄 Nueva sesión", use_container_width=True):
            reset_session()
            st.rerun()
    else:
        st.info("Sin sesión activa")
        if st.button("🚀 Iniciar", use_container_width=True):
            if init_session():
                st.rerun()

# Área principal
if not st.session_state.initialized:
    st.markdown("""
    <div class="welcome-box">
        <h3>👋 Bienvenido al Generador de Presentaciones</h3>
        <p>Este asistente te ayudará a crear presentaciones personalizadas usando IA.</p>
        <p><strong>¿Cómo funciona?</strong></p>
        <ol>
            <li>Haz clic en <strong>"Iniciar"</strong> para preparar el template</li>
            <li>Conversa conmigo sobre el contenido de tu presentación</li>
            <li>Cuando estés listo, di <strong>"generar"</strong> y crearé tu PPT</li>
        </ol>
        <p>👈 Haz clic en <strong>Iniciar</strong> en el sidebar para comenzar.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Mostrar historial de chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])

                # Si es mensaje de generación completa, mostrar botón
                if msg.get("type") == "generation_complete" and msg.get("url"):
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ ¡Presentación generada!</strong><br>
                        <a href="{msg['url']}" target="_blank">Abrir en Google Slides →</a>
                    </div>
                    """, unsafe_allow_html=True)

    # Input de chat
    if prompt := st.chat_input("Escribe tu mensaje..."):
        # Agregar mensaje del usuario
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.write(prompt)

        # Enviar a n8n y obtener respuesta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = send_message(prompt)

            if response.get("type") == "generation_complete":
                # Generación exitosa
                content = response.get("content", "¡Presentación generada!")
                url = response.get("presentationUrl", st.session_state.presentation_url)

                st.write(content)
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ ¡Presentación generada!</strong><br>
                    <a href="{url}" target="_blank">Abrir en Google Slides →</a>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": content,
                    "type": "generation_complete",
                    "url": url
                })

            elif response.get("type") == "error":
                st.error(response.get("content", "Error desconocido"))
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ {response.get('content', 'Error')}"
                })

            else:
                # Mensaje normal
                content = response.get("content", response.get("message", str(response)))
                st.write(content)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": content
                })

# Footer
st.markdown("---")
st.markdown('<div class="cis-footer">Generador de PPT con IA | Powered by n8n + OpenAI | CIS Consultores</div>', unsafe_allow_html=True)
