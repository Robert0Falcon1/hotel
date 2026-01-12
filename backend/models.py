"""
Modelli del Database SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class TipoCamera(enum.Enum):
    """Enumerazione per i tipi di camera"""
    SINGOLA = "singola"
    DOPPIA = "doppia"
    SUITE = "suite"


class StatoPrenotazione(enum.Enum):
    """Enumerazione per gli stati delle prenotazioni"""
    CONFERMATA = "confermata"
    CHECK_IN_EFFETTUATO = "check-in effettuato"
    CHECK_OUT_COMPLETATO = "check-out completato"
    CANCELLATA = "cancellata"


class Camera(Base):
    """Modello per le camere dell'hotel"""
    __tablename__ = 'camere'
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), unique=True, nullable=False, index=True)
    tipo = Column(Enum(TipoCamera), nullable=False)
    piano = Column(Integer, nullable=False)
    prezzo_per_notte = Column(Float, nullable=False)
    servizi_inclusi = Column(Text)
    
    # Relazioni
    prenotazioni = relationship("Prenotazione", back_populates="camera")
    
    def __repr__(self):
        return f"<Camera(numero={self.numero}, tipo={self.tipo.value})>"


class Ospite(Base):
    """Modello per gli ospiti dell'hotel"""
    __tablename__ = 'ospiti'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    documento = Column(String(50), unique=True, nullable=False, index=True)
    nazionalita = Column(String(50), nullable=False)
    email = Column(String(100), index=True)
    telefono = Column(String(20))
    
    # Relazioni
    prenotazioni = relationship("Prenotazione", back_populates="ospite")
    
    def __repr__(self):
        return f"<Ospite(nome={self.nome}, cognome={self.cognome})>"


class Prenotazione(Base):
    """Modello per le prenotazioni"""
    __tablename__ = 'prenotazioni'
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey('camere.id'), nullable=False)
    ospite_id = Column(Integer, ForeignKey('ospiti.id'), nullable=False)
    data_check_in = Column(Date, nullable=False, index=True)
    data_check_out = Column(Date, nullable=False, index=True)
    numero_ospiti = Column(Integer, nullable=False)
    prezzo_totale = Column(Float, nullable=False)
    stato = Column(Enum(StatoPrenotazione), nullable=False, default=StatoPrenotazione.CONFERMATA, index=True)
    
    # Relazioni
    camera = relationship("Camera", back_populates="prenotazioni")
    ospite = relationship("Ospite", back_populates="prenotazioni")
    
    def __repr__(self):
        return f"<Prenotazione(id={self.id}, camera={self.camera_id}, stato={self.stato.value})>"

