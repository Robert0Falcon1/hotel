"""
Pagina Dashboard Personale
"""
import streamlit as st
from frontend.api_client import APIClient
from frontend.components.visualizations import (
    mostra_prenotazione_expander,
    mostra_stato_camera,
    mostra_statistiche
)


def render(api_client: APIClient):
    """
    Renderizza la dashboard per il personale
    
    Args:
        api_client: Client per chiamate API
    """
    st.header("Dashboard Personale Hotel")
    
    # Carica statistiche generali
    stats, errore_stats = api_client.get_statistiche()
    if stats:
        mostra_statistiche(stats)
        st.markdown("---")
    
    # Tab per diverse funzionalità
    tab1, tab2, tab3 = st.tabs([
        "📅 Arrivi e Partenze",
        "🏠 Stato Camere",
        "💰 Report"
    ])
    
    # ========== TAB ARRIVI E PARTENZE ==========
    with tab1:
        col1, col2 = st.columns(2)
        
        # Arrivi
        with col1:
            st.subheader("✈️ Arrivi di Oggi")
            arrivi, errore_arrivi = api_client.get_arrivi_oggi()
            
            if errore_arrivi:
                st.error(f"Errore: {errore_arrivi}")
            elif arrivi:
                for prenotazione in arrivi:
                    if mostra_prenotazione_expander(prenotazione, "arrivo"):
                        # Effettua check-in
                        risultato, errore = api_client.effettua_check_in(prenotazione['id'])
                        if errore:
                            st.error(f"Errore: {errore}")
                        else:
                            st.success(f"✅ {risultato['messaggio']}")
                            st.rerun()
            else:
                st.info("Nessun arrivo previsto per oggi.")
        
        # Partenze
        with col2:
            st.subheader("🎒 Partenze di Oggi")
            partenze, errore_partenze = api_client.get_partenze_oggi()
            
            if errore_partenze:
                st.error(f"Errore: {errore_partenze}")
            elif partenze:
                for prenotazione in partenze:
                    if mostra_prenotazione_expander(prenotazione, "partenza"):
                        # Effettua check-out
                        risultato, errore = api_client.effettua_check_out(prenotazione['id'])
                        if errore:
                            st.error(f"Errore: {errore}")
                        else:
                            st.success(f"✅ {risultato['messaggio']}")
                            st.markdown(f"**Importo:** €{risultato['importo_totale']:.2f}")
                            st.rerun()
            else:
                st.info("Nessuna partenza prevista per oggi.")
    
    # ========== TAB STATO CAMERE ==========
    with tab2:
        st.subheader("🏠 Stato di Occupazione Camere")
        
        stato, errore_stato = api_client.get_stato_occupazione()
        
        if errore_stato:
            st.error(f"Errore: {errore_stato}")
        elif stato:
            # Raggruppa per piano
            piani = {}
            for camera_stato in stato:
                piano = camera_stato['camera']['piano']
                if piano not in piani:
                    piani[piano] = []
                piani[piano].append(camera_stato)
            
            # Mostra per piano
            for piano in sorted(piani.keys()):
                st.markdown(f"### Piano {piano}")
                
                cols = st.columns(4)
                for idx, camera_stato in enumerate(piani[piano]):
                    with cols[idx % 4]:
                        mostra_stato_camera(camera_stato)
                
                st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== TAB REPORT ==========
    with tab3:
        st.subheader("💰 Report e Statistiche")
        
        col_rep1, col_rep2 = st.columns(2)
        
        with col_rep1:
            st.markdown("#### 📊 Statistiche Generali")
            if stats:
                st.json(stats)
        
        with col_rep2:
            st.markdown("#### 🔄 Funzionalità Future")
            st.info("""
            In questa sezione saranno disponibili:
            - Report di fatturazione
            - Statistiche per periodo
            - Export dati Excel/CSV
            - Grafici occupazione
            - Analisi revenue
            """)