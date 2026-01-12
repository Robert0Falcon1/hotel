"""
Componenti form riutilizzabili
"""
import streamlit as st
from datetime import date, timedelta
from typing import Optional, Dict


def form_ricerca_camere() -> Optional[tuple[date, date, str]]:
    """
    Form per ricerca camere disponibili
    
    Returns:
        Tuple (data_check_in, data_check_out, tipo_camera) o None
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_arrivo = st.date_input(
            "Data Check-in",
            value=date.today(),
            min_value=date.today(),
            key="ricerca_check_in"
        )
    
    with col2:
        data_partenza = st.date_input(
            "Data Check-out",
            value=date.today() + timedelta(days=2),
            min_value=date.today() + timedelta(days=1),
            key="ricerca_check_out"
        )
    
    with col3:
        tipo_camera = st.selectbox(
            "Tipo Camera",
            ["Tutte", "Singola", "Doppia", "Suite"],
            key="ricerca_tipo"
        )
    
    if st.button("🔎 Cerca Camere", type="primary", use_container_width=True):
        if data_arrivo >= data_partenza:
            st.error("❌ La data di check-out deve essere successiva al check-in!")
            return None
        return data_arrivo, data_partenza, tipo_camera
    
    return None


def form_dati_ospite(camera_id: int) -> Optional[Dict]:
    """
    Form per inserimento dati ospite
    
    Args:
        camera_id: ID della camera per cui creare la prenotazione
        
    Returns:
        Dizionario con i dati dell'ospite o None
    """
    with st.form(key=f'form_prenotazione_{camera_id}'):
        st.markdown("#### 📝 Dati Ospite")
        
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome*", key=f"nome_{camera_id}")
            cognome = st.text_input("Cognome*", key=f"cognome_{camera_id}")
            documento = st.text_input("Numero Documento*", key=f"doc_{camera_id}")
        
        with col_b:
            nazionalita = st.text_input("Nazionalità*", key=f"naz_{camera_id}")
            email = st.text_input("Email", key=f"email_{camera_id}")
            telefono = st.text_input("Telefono", key=f"tel_{camera_id}")
        
        numero_ospiti = st.number_input(
            "Numero Ospiti*",
            min_value=1,
            max_value=4,
            value=1,
            key=f"num_ospiti_{camera_id}"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            conferma = st.form_submit_button(
                "✅ Conferma Prenotazione",
                type="primary",
                use_container_width=True
            )
        with col_btn2:
            annulla = st.form_submit_button("❌ Annulla", use_container_width=True)
        
        if conferma:
            if not all([nome, cognome, documento, nazionalita]):
                st.error("❌ Compila tutti i campi obbligatori!")
                return None
            
            return {
                "dati_ospite": {
                    "nome": nome,
                    "cognome": cognome,
                    "documento": documento,
                    "nazionalita": nazionalita,
                    "email": email if email else None,
                    "telefono": telefono if telefono else None
                },
                "numero_ospiti": numero_ospiti,
                "conferma": True
            }
        
        if annulla:
            return {"annulla": True}
    
    return None