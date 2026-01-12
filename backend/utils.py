"""
Funzioni di utilità
"""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.models import Prenotazione, StatoPrenotazione


def calcola_prezzo_totale(prezzo_per_notte: float, data_check_in: date, data_check_out: date) -> float:
    """
    Calcola il prezzo totale in base ai giorni di permanenza
    
    Args:
        prezzo_per_notte: Prezzo per notte della camera
        data_check_in: Data di check-in
        data_check_out: Data di check-out
        
    Returns:
        Prezzo totale calcolato
    """
    giorni = (data_check_out - data_check_in).days
    return round(prezzo_per_notte * giorni, 2)


def verifica_disponibilita_camera(
    db: Session,
    camera_id: int,
    data_check_in: date,
    data_check_out: date,
    escludi_prenotazione_id: Optional[int] = None
) -> bool:
    """
    Verifica se una camera è disponibile per il periodo richiesto
    
    Args:
        db: Sessione database
        camera_id: ID della camera da verificare
        data_check_in: Data di check-in desiderata
        data_check_out: Data di check-out desiderata
        escludi_prenotazione_id: ID prenotazione da escludere (per modifiche)
        
    Returns:
        True se disponibile, False altrimenti
    """
    query = db.query(Prenotazione).filter(
        Prenotazione.camera_id == camera_id,
        Prenotazione.stato.in_([
            StatoPrenotazione.CONFERMATA,
            StatoPrenotazione.CHECK_IN_EFFETTUATO
        ]),
        or_(
            # Caso 1: check-in richiesto durante prenotazione esistente
            and_(
                Prenotazione.data_check_in <= data_check_in,
                Prenotazione.data_check_out > data_check_in
            ),
            # Caso 2: check-out richiesto durante prenotazione esistente
            and_(
                Prenotazione.data_check_in < data_check_out,
                Prenotazione.data_check_out >= data_check_out
            ),
            # Caso 3: prenotazione richiesta contiene prenotazione esistente
            and_(
                Prenotazione.data_check_in >= data_check_in,
                Prenotazione.data_check_out <= data_check_out
            )
        )
    )
    
    if escludi_prenotazione_id:
        query = query.filter(Prenotazione.id != escludi_prenotazione_id)
    
    return query.count() == 0


def valida_date_prenotazione(data_check_in: date, data_check_out: date) -> tuple[bool, Optional[str]]:
    """
    Valida le date di una prenotazione
    
    Args:
        data_check_in: Data di check-in
        data_check_out: Data di check-out
        
    Returns:
        Tupla (valido, messaggio_errore)
    """
    if data_check_in >= data_check_out:
        return False, "La data di check-out deve essere successiva al check-in"
    
    if data_check_in < date.today():
        return False, "La data di check-in non può essere nel passato"
    
    giorni = (data_check_out - data_check_in).days
    if giorni > 30:
        return False, "Il periodo massimo di prenotazione è 30 giorni"
    
    return True, None
