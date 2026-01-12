"""
Client per interagire con l'API Backend
"""
import requests
from datetime import date
from typing import List, Dict, Optional
from frontend.config import API_URL


class APIClient:
    """Client per chiamate API"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
    
    def _handle_response(self, response: requests.Response):
        """Gestisce la risposta dell'API"""
        if response.status_code >= 400:
            error_detail = response.json().get('detail', 'Errore sconosciuto')
            return None, error_detail
        return response.json(), None
    
    # ========== CAMERE ==========
    def get_camere(self) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Ottiene tutte le camere"""
        try:
            response = requests.get(f"{self.base_url}/camere")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def get_camera(self, camera_id: int) -> tuple[Optional[Dict], Optional[str]]:
        """Ottiene una camera specifica"""
        try:
            response = requests.get(f"{self.base_url}/camere/{camera_id}")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def cerca_camere_disponibili(
        self,
        data_check_in: date,
        data_check_out: date,
        tipo: Optional[str] = None
    ) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Cerca camere disponibili"""
        try:
            payload = {
                "data_check_in": str(data_check_in),
                "data_check_out": str(data_check_out)
            }
            if tipo and tipo != "Tutte":
                payload["tipo"] = tipo.lower()
            
            response = requests.post(
                f"{self.base_url}/camere/disponibili",
                json=payload
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    # ========== PRENOTAZIONI ==========
    def crea_prenotazione(
        self,
        camera_id: int,
        ospite_data: Dict,
        data_check_in: date,
        data_check_out: date,
        numero_ospiti: int
    ) -> tuple[Optional[Dict], Optional[str]]:
        """Crea una nuova prenotazione"""
        try:
            payload = {
                "camera_id": camera_id,
                "ospite": ospite_data,
                "data_check_in": str(data_check_in),
                "data_check_out": str(data_check_out),
                "numero_ospiti": numero_ospiti
            }
            response = requests.post(
                f"{self.base_url}/prenotazioni",
                json=payload
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def get_prenotazione(self, prenotazione_id: int) -> tuple[Optional[Dict], Optional[str]]:
        """Ottiene una prenotazione specifica"""
        try:
            response = requests.get(f"{self.base_url}/prenotazioni/{prenotazione_id}")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def modifica_prenotazione(
        self,
        prenotazione_id: int,
        aggiornamento: Dict
    ) -> tuple[Optional[Dict], Optional[str]]:
        """Modifica una prenotazione"""
        try:
            response = requests.put(
                f"{self.base_url}/prenotazioni/{prenotazione_id}",
                json=aggiornamento
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def effettua_check_in(self, prenotazione_id: int) -> tuple[Optional[Dict], Optional[str]]:
        """Effettua check-in"""
        try:
            response = requests.post(
                f"{self.base_url}/prenotazioni/{prenotazione_id}/check-in"
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def effettua_check_out(self, prenotazione_id: int) -> tuple[Optional[Dict], Optional[str]]:
        """Effettua check-out"""
        try:
            response = requests.post(
                f"{self.base_url}/prenotazioni/{prenotazione_id}/check-out"
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def cancella_prenotazione(self, prenotazione_id: int) -> tuple[Optional[Dict], Optional[str]]:
        """Cancella una prenotazione"""
        try:
            response = requests.delete(
                f"{self.base_url}/prenotazioni/{prenotazione_id}"
            )
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    # ========== DASHBOARD ==========
    def get_arrivi_oggi(self) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Ottiene arrivi di oggi"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/arrivi-oggi")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def get_partenze_oggi(self) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Ottiene partenze di oggi"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/partenze-oggi")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def get_stato_occupazione(self) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Ottiene stato occupazione"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/occupazione")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
    
    def get_statistiche(self) -> tuple[Optional[Dict], Optional[str]]:
        """Ottiene statistiche generali"""
        try:
            response = requests.get(f"{self.base_url}/dashboard/statistiche")
            return self._handle_response(response)
        except Exception as e:
            return None, str(e)
