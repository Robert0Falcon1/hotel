"""
Configurazione frontend
"""
import os
from dotenv import load_dotenv

load_dotenv()

# URL API Backend
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Configurazione pagina Streamlit
PAGE_CONFIG = {
    "page_title": "Hotel Management System",
    "page_icon": "🏨",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Stili CSS personalizzati
CUSTOM_CSS = """
<style>
.camera-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}

.camera-disponibile {
    background-color: #ccffcc;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 5px;
}

.camera-occupata {
    background-color: #ffcccc;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 5px;
}

.stat-card {
    background-color: #e1f5ff;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}

.success-box {
    background-color: #d4edda;
    border-left: 5px solid #28a745;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}

.warning-box {
    background-color: #fff3cd;
    border-left: 5px solid #ffc107;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
</style>
"""