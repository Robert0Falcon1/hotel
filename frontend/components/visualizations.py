"""
Componenti per visualizzazione dati
"""
import streamlit as st
from typing import List, Dict


def mostra_camera_card(camera: Dict, giorni: int):
    """
    Mostra una card per una camera disponibile
    
    Args:
        camera: Dati della camera
        giorni: Numero di giorni di soggiorno
    """
    with st.container():
        st.markdown("---")
        col_info, col_azione = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"### 🚪 Camera {camera['numero']} - {camera['tipo'].title()}")
            st.markdown(f"**Piano:** {camera['piano']}")
            st.markdown(f"**Prezzo per notte:** €{camera['prezzo_per_notte']:.2f}")
            st.markdown(f"**Prezzo totale ({giorni} notti):** €{camera['prezzo_per_notte'] * giorni:.2f}")
            st.markdown(f"**Servizi inclusi:** {camera['servizi_inclusi']}")
        
        with col_azione:
            st.markdown("<br>", unsafe_allow_html=True)
            return st.button(
                "Prenota",
                key=f"prenota_{camera['id']}",
                type="primary"
            )


def mostra_stato_camera(camera_stato: Dict):
    """
    Mostra lo stato di una camera (occupata/libera)
    
    Args:
        camera_stato: Stato della camera
    """
    camera = camera_stato['camera']
    if camera_stato['occupata']:
        st.markdown(
            f"""
            <div class="camera-occupata">
                <h4>🔴 Camera {camera['numero']}</h4>
                <p><b>{camera['tipo'].title()}</b></p>
                <p><b>Ospite:</b><br>{camera_stato['ospite']}</p>
                <p><b>Check-out:</b><br>{camera_stato['check_out_previsto']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="camera-disponibile">
                <h4>🟢 Camera {camera['numero']}</h4>
                <p><b>{camera['tipo'].title()}</b></p>
                <p><b>Disponibile</b></p>
                <p>€{camera['prezzo_per_notte']:.2f}/notte</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def mostra_statistiche(stats: Dict):
    """
    Mostra statistiche generali
    
    Args:
        stats: Dizionario con le statistiche
    """
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Totale Camere", stats['totale_camere'])
    with col2:
        st.metric("Camere Occupate", stats['camere_occupate'])
    with col3:
        st.metric("Camere Libere", stats['camere_libere'])
    with col4:
        st.metric("Tasso Occupazione", f"{stats['tasso_occupazione']:.1f}%")
    with col5:
        st.metric("Prenotazioni Future", stats['prenotazioni_future'])


def mostra_prenotazione_expander(prenotazione: Dict, tipo: str = "arrivo"):
    """
    Mostra i dettagli di una prenotazione in un expander
    
    Args:
        prenotazione: Dati della prenotazione
        tipo: "arrivo" o "partenza"
    
    Returns:
        True se è stato richiesto check-in/out
    """
    titolo = f"Camera {prenotazione['camera']['numero']} - {prenotazione['ospite']['nome']} {prenotazione['ospite']['cognome']}"
    
    with st.expander(titolo):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Ospite:** {prenotazione['ospite']['nome']} {prenotazione['ospite']['cognome']}")
            st.markdown(f"**Documento:** {prenotazione['ospite']['documento']}")
            st.markdown(f"**Nazionalità:** {prenotazione['ospite']['nazionalita']}")
        
        with col2:
            st.markdown(f"**Email:** {prenotazione['ospite']['email'] or 'N/D'}")
            st.markdown(f"**Telefono:** {prenotazione['ospite']['telefono'] or 'N/D'}")
            st.markdown(f"**Numero Ospiti:** {prenotazione['numero_ospiti']}")
        
        st.markdown("---")
        
        if tipo == "arrivo":
            st.markdown(f"**Check-out previsto:** {prenotazione['data_check_out']}")
            return st.button(
                "✅ Effettua Check-in",
                key=f"checkin_{prenotazione['id']}",
                type="primary"
            )
        else:  # partenza
            st.markdown(f"**Check-in:** {prenotazione['data_check_in']}")
            st.markdown(f"**Importo totale:** €{prenotazione['prezzo_totale']:.2f}")
            return st.button(
                "🚪 Effettua Check-out",
                key=f"checkout_{prenotazione['id']}",
                type="primary"
            )
    
    return False