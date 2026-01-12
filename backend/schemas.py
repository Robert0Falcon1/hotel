"""
Schemi Pydantic per validazione e serializzazione
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional


class CameraBase(BaseModel):
    """Schema base per Camera"""
    numero: str = Field(..., min_length=1, max_length=10)
    tipo: str
    piano: int = Field(..., ge=0)
    prezzo_per_notte: float = Field(..., gt=0)
    servizi_inclusi: str


class CameraCreate(CameraBase):
    """Schema per creazione Camera"""
    pass


class CameraResponse(CameraBase):
    """Schema per risposta Camera"""
    id: int
    
    class Config:
        from_attributes = True


class OspiteBase(BaseModel):
    """Schema base per Ospite"""
    nome: str = Field(..., min_length=1, max_length=100)
    cognome: str = Field(..., min_length=1, max_length=100)
    documento: str = Field(..., min_length=5, max_length=50)
    nazionalita: str = Field(..., min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)


class OspiteCreate(OspiteBase):
    """Schema per creazione Ospite"""
    pass


class OspiteResponse(OspiteBase):
    """Schema per risposta Ospite"""
    id: int
    
    class Config:
        from_attributes = True


class PrenotazioneBase(BaseModel):
    """Schema base per Prenotazione"""
    camera_id: int
    data_check_in: date
    data_check_out: date
    numero_ospiti: int = Field(..., ge=1, le=10)


class PrenotazioneCreate(PrenotazioneBase):
    """Schema per creazione Prenotazione"""
    ospite: OspiteCreate


class PrenotazioneUpdate(BaseModel):
    """Schema per aggiornamento Prenotazione"""
    data_check_in: Optional[date] = None
    data_check_out: Optional[date] = None
    numero_ospiti: Optional[int] = Field(None, ge=1, le=10)


class PrenotazioneResponse(BaseModel):
    """Schema per risposta Prenotazione"""
    id: int
    camera_id: int
    ospite_id: int
    data_check_in: date
    data_check_out: date
    numero_ospiti: int
    prezzo_totale: float
    stato: str
    camera: CameraResponse
    ospite: OspiteResponse
    
    class Config:
        from_attributes = True


class RicercaCamereRequest(BaseModel):
    """Schema per richiesta ricerca camere"""
    data_check_in: date
    data_check_out: date
    tipo: Optional[str] = None


class StatoOccupazioneResponse(BaseModel):
    """Schema per risposta stato occupazione"""
    camera: CameraResponse
    occupata: bool
    ospite: Optional[str] = None
    check_out_previsto: Optional[str] = None

