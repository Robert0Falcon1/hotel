"""
Applicazione Streamlit principale
"""
import streamlit as st
from frontend.config import PAGE_CONFIG, CUSTOM_CSS, API_URL
from frontend.api_client import APIClient
from frontend.pages import ospiti, personale

# Configurazione pagina
st.set_page_config(**PAGE_CONFIG)

# Applica CSS personalizzato
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Inizializza API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

# Interfaccia principale
st.title("🏨 Sistema di Gestione Hotel")

# Sidebar per selezione modalità
st.sidebar.image("https://via.placeholder.com/300x100/1e3a8a/ffffff?text=Hotel+Management", use_container_width=True)
st.sidebar.markdown("---")

modalita = st.sidebar.radio(
    "Seleziona Modalità",
    ["👤 Portale Ospiti", "🔧 Dashboard Personale"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Backend API:** {API_URL}")
st.sidebar.markdown("**Versione:** 1.0.0")

# Router tra modalità
if modalita == "👤 Portale Ospiti":
    ospiti.render(st.session_state.api_client)
else:
    personale.render(st.session_state.api_client)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray;">
        Sistema di Gestione Hotel v1.0 | Sviluppato con ❤️ usando Python, FastAPI e Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
