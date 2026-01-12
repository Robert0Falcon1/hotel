"""
Pagina Portale Ospiti
"""
import streamlit as st
from datetime import timedelta
from frontend.api_client import APIClient
from frontend.components.forms import form_ricerca_camere, form_dati_ospite
from frontend.components.visualizations import mostra_camera_card


def render(api_client: APIClient):
    """
    Renderizza la pagina per gli ospiti
    
    Args:
        api_client: Client per chiamate API
    """
    st.header("Benvenuto nel nostro Hotel!")
    st.markdown("Cerca e prenota la camera perfetta per il tuo soggiorno.")
    
    # Sezione ricerca camere
    st.subheader("🔍 Cerca Camere Disponibili")
    
    risultato_ricerca = form_ricerca_camere()
    
    if risultato_ricerca:
        data_arrivo, data_partenza, tipo_camera = risultato_ricerca
        
        with st.spinner("Ricerca camere disponibili..."):
            camere, errore = api_client.cerca_camere_disponibili(
                data_arrivo,
                data_partenza,
                tipo_camera
            )
        
        if errore:
            st.error(f"❌ Errore: {errore}")
        elif camere:
            st.success(f"✅ Trovate {len(camere)} camere disponibili!")
            
            giorni = (data_partenza - data_arrivo).days
            
            for camera in camere:
                # Mostra card camera
                prenota_cliccato = mostra_camera_card(camera, giorni)
                
                # Gestisci click prenota
                if prenota_cliccato:
                    st.session_state[f'prenota_camera_{camera["id"]}'] = True
                
                # Mostra form prenotazione se richiesto
                if st.session_state.get(f'prenota_camera_{camera["id"]}', False):
                    risultato_form = form_dati_ospite(camera['id'])
                    
                    if risultato_form:
                        if risultato_form.get('annulla'):
                            st.session_state[f'prenota_camera_{camera["id"]}'] = False
                            st.rerun()
                        
                        elif risultato_form.get('conferma'):
                            # Crea prenotazione
                            prenotazione, errore_pren = api_client.crea_prenotazione(
                                camera['id'],
                                risultato_form['dati_ospite'],
                                data_arrivo,
                                data_partenza,
                                risultato_form['numero_ospiti']
                            )
                            
                            if errore_pren:
                                st.error(f"❌ Errore nella prenotazione: {errore_pren}")
                            else:
                                st.success("✅ Prenotazione confermata con successo!")
                                st.balloons()
                                
                                # Mostra riepilogo
                                st.markdown(
                                    f"""
                                    <div class="success-box">
                                        <h4>📋 Riepilogo Prenotazione</h4>
                                        <p><b>ID Prenotazione:</b> {prenotazione['id']}</p>
                                        <p><b>Camera:</b> {camera['numero']} - {camera['tipo'].title()}</p>
                                        <p><b>Check-in:</b> {data_arrivo}</p>
                                        <p><b>Check-out:</b> {data_partenza}</p>
                                        <p><b>Importo Totale:</b> €{prenotazione['prezzo_totale']:.2f}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                st.session_state[f'prenota_camera_{camera["id"]}'] = False
                                st.info("💡 Conserva il tuo ID prenotazione per il check-in")
        else:
            st.warning("😔 Nessuna camera disponibile per il periodo selezionato. Prova con date diverse.")
