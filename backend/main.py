# main.py - API REST con FastAPI
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import (
    Camera, Ospite, Prenotazione, TipoCamera, StatoPrenotazione,
    get_db, init_db
)

# Inizializza il database
init_db()

app = FastAPI(title="Sistema Gestione Hotel", version="1.0.0")

# Configurazione CORS per permettere richieste da Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemi Pydantic per validazione input/output
class CameraResponse(BaseModel):
    id: int
    numero: str
    tipo: str
    piano: int
    prezzo_per_notte: float
    servizi_inclusi: str
    
    class Config:
        from_attributes = True

class OspiteCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    cognome: str = Field(..., min_length=1)
    documento: str = Field(..., min_length=5)
    nazionalita: str = Field(..., min_length=2)
    email: Optional[str] = None
    telefono: Optional[str] = None

class OspiteResponse(BaseModel):
    id: int
    nome: str
    cognome: str
    documento: str
    nazionalita: str
    email: Optional[str]
    telefono: Optional[str]
    
    class Config:
        from_attributes = True

class PrenotazioneCreate(BaseModel):
    camera_id: int
    ospite: OspiteCreate
    data_check_in: date
    data_check_out: date
    numero_ospiti: int = Field(..., ge=1)

class PrenotazioneUpdate(BaseModel):
    data_check_in: Optional[date] = None
    data_check_out: Optional[date] = None
    numero_ospiti: Optional[int] = None

class PrenotazioneResponse(BaseModel):
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
    data_check_in: date
    data_check_out: date
    tipo: Optional[str] = None

# Funzioni di utilità
def calcola_prezzo_totale(prezzo_per_notte: float, data_check_in: date, data_check_out: date) -> float:
    """Calcola il prezzo totale in base ai giorni di permanenza"""
    giorni = (data_check_out - data_check_in).days
    return prezzo_per_notte * giorni

def verifica_disponibilita_camera(
    db: Session, 
    camera_id: int, 
    data_check_in: date, 
    data_check_out: date,
    escludi_prenotazione_id: Optional[int] = None
) -> bool:
    """Verifica se una camera è disponibile per il periodo richiesto"""
    query = db.query(Prenotazione).filter(
        Prenotazione.camera_id == camera_id,
        Prenotazione.stato.in_([
            StatoPrenotazione.CONFERMATA,
            StatoPrenotazione.CHECK_IN_EFFETTUATO
        ]),
        or_(
            and_(
                Prenotazione.data_check_in <= data_check_in,
                Prenotazione.data_check_out > data_check_in
            ),
            and_(
                Prenotazione.data_check_in < data_check_out,
                Prenotazione.data_check_out >= data_check_out
            ),
            and_(
                Prenotazione.data_check_in >= data_check_in,
                Prenotazione.data_check_out <= data_check_out
            )
        )
    )
    
    if escludi_prenotazione_id:
        query = query.filter(Prenotazione.id != escludi_prenotazione_id)
    
    return query.count() == 0

# Endpoint API
@app.get("/")
def root():
    return {"messaggio": "API Sistema Gestione Hotel", "versione": "1.0.0"}

@app.get("/camere", response_model=List[CameraResponse])
def ottieni_camere(db: Session = Depends(get_db)):
    """Ottiene l'elenco di tutte le camere"""
    camere = db.query(Camera).all()
    return [CameraResponse(
        id=c.id,
        numero=c.numero,
        tipo=c.tipo.value,
        piano=c.piano,
        prezzo_per_notte=c.prezzo_per_notte,
        servizi_inclusi=c.servizi_inclusi
    ) for c in camere]

@app.post("/camere/disponibili", response_model=List[CameraResponse])
def cerca_camere_disponibili(
    ricerca: RicercaCamereRequest,
    db: Session = Depends(get_db)
):
    """Cerca camere disponibili per tipo e date specifiche"""
    if ricerca.data_check_in >= ricerca.data_check_out:
        raise HTTPException(400, "La data di check-out deve essere successiva al check-in")
    
    if ricerca.data_check_in < date.today():
        raise HTTPException(400, "La data di check-in non può essere nel passato")
    
    # Query per tutte le camere del tipo richiesto (se specificato)
    query = db.query(Camera)
    if ricerca.tipo:
        try:
            tipo_enum = TipoCamera(ricerca.tipo)
            query = query.filter(Camera.tipo == tipo_enum)
        except ValueError:
            raise HTTPException(400, f"Tipo camera non valido: {ricerca.tipo}")
    
    camere = query.all()
    
    # Filtra le camere disponibili
    camere_disponibili = []
    for camera in camere:
        if verifica_disponibilita_camera(
            db, 
            camera.id, 
            ricerca.data_check_in, 
            ricerca.data_check_out
        ):
            camere_disponibili.append(CameraResponse(
                id=camera.id,
                numero=camera.numero,
                tipo=camera.tipo.value,
                piano=camera.piano,
                prezzo_per_notte=camera.prezzo_per_notte,
                servizi_inclusi=camera.servizi_inclusi
            ))
    
    return camere_disponibili

@app.post("/prenotazioni", response_model=PrenotazioneResponse)
def crea_prenotazione(
    prenotazione: PrenotazioneCreate,
    db: Session = Depends(get_db)
):
    """Crea una nuova prenotazione verificando la disponibilità"""
    # Validazioni
    if prenotazione.data_check_in >= prenotazione.data_check_out:
        raise HTTPException(400, "La data di check-out deve essere successiva al check-in")
    
    if prenotazione.data_check_in < date.today():
        raise HTTPException(400, "La data di check-in non può essere nel passato")
    
    # Verifica esistenza camera
    camera = db.query(Camera).filter(Camera.id == prenotazione.camera_id).first()
    if not camera:
        raise HTTPException(404, "Camera non trovata")
    
    # Verifica disponibilità
    if not verifica_disponibilita_camera(
        db,
        prenotazione.camera_id,
        prenotazione.data_check_in,
        prenotazione.data_check_out
    ):
        raise HTTPException(409, "Camera non disponibile per il periodo richiesto")
    
    # Crea o trova ospite
    ospite_esistente = db.query(Ospite).filter(
        Ospite.documento == prenotazione.ospite.documento
    ).first()
    
    if ospite_esistente:
        ospite = ospite_esistente
    else:
        ospite = Ospite(**prenotazione.ospite.dict())
        db.add(ospite)
        db.flush()
    
    # Calcola prezzo totale
    prezzo_totale = calcola_prezzo_totale(
        camera.prezzo_per_notte,
        prenotazione.data_check_in,
        prenotazione.data_check_out
    )
    
    # Crea prenotazione
    nuova_prenotazione = Prenotazione(
        camera_id=prenotazione.camera_id,
        ospite_id=ospite.id,
        data_check_in=prenotazione.data_check_in,
        data_check_out=prenotazione.data_check_out,
        numero_ospiti=prenotazione.numero_ospiti,
        prezzo_totale=prezzo_totale,
        stato=StatoPrenotazione.CONFERMATA
    )
    
    db.add(nuova_prenotazione)
    db.commit()
    db.refresh(nuova_prenotazione)
    
    return PrenotazioneResponse(
        id=nuova_prenotazione.id,
        camera_id=nuova_prenotazione.camera_id,
        ospite_id=nuova_prenotazione.ospite_id,
        data_check_in=nuova_prenotazione.data_check_in,
        data_check_out=nuova_prenotazione.data_check_out,
        numero_ospiti=nuova_prenotazione.numero_ospiti,
        prezzo_totale=nuova_prenotazione.prezzo_totale,
        stato=nuova_prenotazione.stato.value,
        camera=CameraResponse(
            id=camera.id,
            numero=camera.numero,
            tipo=camera.tipo.value,
            piano=camera.piano,
            prezzo_per_notte=camera.prezzo_per_notte,
            servizi_inclusi=camera.servizi_inclusi
        ),
        ospite=OspiteResponse(
            id=ospite.id,
            nome=ospite.nome,
            cognome=ospite.cognome,
            documento=ospite.documento,
            nazionalita=ospite.nazionalita,
            email=ospite.email,
            telefono=ospite.telefono
        )
    )

@app.get("/prenotazioni/{prenotazione_id}", response_model=PrenotazioneResponse)
def ottieni_prenotazione(prenotazione_id: int, db: Session = Depends(get_db)):
    """Ottiene i dettagli di una prenotazione specifica"""
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
    if not prenotazione:
        raise HTTPException(404, "Prenotazione non trovata")
    
    return PrenotazioneResponse(
        id=prenotazione.id,
        camera_id=prenotazione.camera_id,
        ospite_id=prenotazione.ospite_id,
        data_check_in=prenotazione.data_check_in,
        data_check_out=prenotazione.data_check_out,
        numero_ospiti=prenotazione.numero_ospiti,
        prezzo_totale=prenotazione.prezzo_totale,
        stato=prenotazione.stato.value,
        camera=CameraResponse(
            id=prenotazione.camera.id,
            numero=prenotazione.camera.numero,
            tipo=prenotazione.camera.tipo.value,
            piano=prenotazione.camera.piano,
            prezzo_per_notte=prenotazione.camera.prezzo_per_notte,
            servizi_inclusi=prenotazione.camera.servizi_inclusi
        ),
        ospite=OspiteResponse(
            id=prenotazione.ospite.id,
            nome=prenotazione.ospite.nome,
            cognome=prenotazione.ospite.cognome,
            documento=prenotazione.ospite.documento,
            nazionalita=prenotazione.ospite.nazionalita,
            email=prenotazione.ospite.email,
            telefono=prenotazione.ospite.telefono
        )
    )

@app.put("/prenotazioni/{prenotazione_id}", response_model=PrenotazioneResponse)
def modifica_prenotazione(
    prenotazione_id: int,
    aggiornamento: PrenotazioneUpdate,
    db: Session = Depends(get_db)
):
    """Modifica una prenotazione esistente"""
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
    if not prenotazione:
        raise HTTPException(404, "Prenotazione non trovata")
    
    if prenotazione.stato == StatoPrenotazione.CANCELLATA:
        raise HTTPException(400, "Non è possibile modificare una prenotazione cancellata")
    
    if prenotazione.stato == StatoPrenotazione.CHECK_OUT_COMPLETATO:
        raise HTTPException(400, "Non è possibile modificare una prenotazione completata")
    
    # Aggiorna date se fornite
    nuova_check_in = aggiornamento.data_check_in or prenotazione.data_check_in
    nuova_check_out = aggiornamento.data_check_out or prenotazione.data_check_out
    
    if nuova_check_in >= nuova_check_out:
        raise HTTPException(400, "La data di check-out deve essere successiva al check-in")
    
    # Verifica disponibilità se le date sono cambiate
    if (aggiornamento.data_check_in or aggiornamento.data_check_out):
        if not verifica_disponibilita_camera(
            db,
            prenotazione.camera_id,
            nuova_check_in,
            nuova_check_out,
            escludi_prenotazione_id=prenotazione_id
        ):
            raise HTTPException(409, "Camera non disponibile per il nuovo periodo")
        
        # Ricalcola prezzo
        camera = prenotazione.camera
        prenotazione.prezzo_totale = calcola_prezzo_totale(
            camera.prezzo_per_notte,
            nuova_check_in,
            nuova_check_out
        )
    
    if aggiornamento.data_check_in:
        prenotazione.data_check_in = aggiornamento.data_check_in
    if aggiornamento.data_check_out:
        prenotazione.data_check_out = aggiornamento.data_check_out
    if aggiornamento.numero_ospiti:
        prenotazione.numero_ospiti = aggiornamento.numero_ospiti
    
    db.commit()
    db.refresh(prenotazione)
    
    return PrenotazioneResponse(
        id=prenotazione.id,
        camera_id=prenotazione.camera_id,
        ospite_id=prenotazione.ospite_id,
        data_check_in=prenotazione.data_check_in,
        data_check_out=prenotazione.data_check_out,
        numero_ospiti=prenotazione.numero_ospiti,
        prezzo_totale=prenotazione.prezzo_totale,
        stato=prenotazione.stato.value,
        camera=CameraResponse(
            id=prenotazione.camera.id,
            numero=prenotazione.camera.numero,
            tipo=prenotazione.camera.tipo.value,
            piano=prenotazione.camera.piano,
            prezzo_per_notte=prenotazione.camera.prezzo_per_notte,
            servizi_inclusi=prenotazione.camera.servizi_inclusi
        ),
        ospite=OspiteResponse(
            id=prenotazione.ospite.id,
            nome=prenotazione.ospite.nome,
            cognome=prenotazione.ospite.cognome,
            documento=prenotazione.ospite.documento,
            nazionalita=prenotazione.ospite.nazionalita,
            email=prenotazione.ospite.email,
            telefono=prenotazione.ospite.telefono
        )
    )

@app.post("/prenotazioni/{prenotazione_id}/check-in")
def effettua_check_in(prenotazione_id: int, db: Session = Depends(get_db)):
    """Effettua il check-in per una prenotazione"""
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
    if not prenotazione:
        raise HTTPException(404, "Prenotazione non trovata")
    
    if prenotazione.stato != StatoPrenotazione.CONFERMATA:
        raise HTTPException(400, f"Check-in non possibile. Stato attuale: {prenotazione.stato.value}")
    
    prenotazione.stato = StatoPrenotazione.CHECK_IN_EFFETTUATO
    db.commit()
    
    return {"messaggio": "Check-in effettuato con successo", "prenotazione_id": prenotazione_id}

@app.post("/prenotazioni/{prenotazione_id}/check-out")
def effettua_check_out(prenotazione_id: int, db: Session = Depends(get_db)):
    """Effettua il check-out per una prenotazione"""
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
    if not prenotazione:
        raise HTTPException(404, "Prenotazione non trovata")
    
    if prenotazione.stato != StatoPrenotazione.CHECK_IN_EFFETTUATO:
        raise HTTPException(400, f"Check-out non possibile. Stato attuale: {prenotazione.stato.value}")
    
    prenotazione.stato = StatoPrenotazione.CHECK_OUT_COMPLETATO
    db.commit()
    
    return {
        "messaggio": "Check-out completato con successo",
        "prenotazione_id": prenotazione_id,
        "importo_totale": prenotazione.prezzo_totale
    }

@app.delete("/prenotazioni/{prenotazione_id}")
def cancella_prenotazione(prenotazione_id: int, db: Session = Depends(get_db)):
    """Cancella una prenotazione"""
    prenotazione = db.query(Prenotazione).filter(Prenotazione.id == prenotazione_id).first()
    if not prenotazione:
        raise HTTPException(404, "Prenotazione non trovata")
    
    if prenotazione.stato == StatoPrenotazione.CHECK_OUT_COMPLETATO:
        raise HTTPException(400, "Non è possibile cancellare una prenotazione completata")
    
    prenotazione.stato = StatoPrenotazione.CANCELLATA
    db.commit()
    
    return {"messaggio": "Prenotazione cancellata con successo"}

@app.get("/dashboard/arrivi-oggi", response_model=List[PrenotazioneResponse])
def arrivi_oggi(db: Session = Depends(get_db)):
    """Ottiene le prenotazioni con check-in previsto per oggi"""
    oggi = date.today()
    prenotazioni = db.query(Prenotazione).filter(
        Prenotazione.data_check_in == oggi,
        Prenotazione.stato == StatoPrenotazione.CONFERMATA
    ).all()
    
    return [PrenotazioneResponse(
        id=p.id,
        camera_id=p.camera_id,
        ospite_id=p.ospite_id,
        data_check_in=p.data_check_in,
        data_check_out=p.data_check_out,
        numero_ospiti=p.numero_ospiti,
        prezzo_totale=p.prezzo_totale,
        stato=p.stato.value,
        camera=CameraResponse(
            id=p.camera.id,
            numero=p.camera.numero,
            tipo=p.camera.tipo.value,
            piano=p.camera.piano,
            prezzo_per_notte=p.camera.prezzo_per_notte,
            servizi_inclusi=p.camera.servizi_inclusi
        ),
        ospite=OspiteResponse(
            id=p.ospite.id,
            nome=p.ospite.nome,
            cognome=p.ospite.cognome,
            documento=p.ospite.documento,
            nazionalita=p.ospite.nazionalita,
            email=p.ospite.email,
            telefono=p.ospite.telefono
        )
    ) for p in prenotazioni]

@app.get("/dashboard/partenze-oggi", response_model=List[PrenotazioneResponse])
def partenze_oggi(db: Session = Depends(get_db)):
    """Ottiene le prenotazioni con check-out previsto per oggi"""
    oggi = date.today()
    prenotazioni = db.query(Prenotazione).filter(
        Prenotazione.data_check_out == oggi,
        Prenotazione.stato == StatoPrenotazione.CHECK_IN_EFFETTUATO
    ).all()
    
    return [PrenotazioneResponse(
        id=p.id,
        camera_id=p.camera_id,
        ospite_id=p.ospite_id,
        data_check_in=p.data_check_in,
        data_check_out=p.data_check_out,
        numero_ospiti=p.numero_ospiti,
        prezzo_totale=p.prezzo_totale,
        stato=p.stato.value,
        camera=CameraResponse(
            id=p.camera.id,
            numero=p.camera.numero,
            tipo=p.camera.tipo.value,
            piano=p.camera.piano,
            prezzo_per_notte=p.camera.prezzo_per_notte,
            servizi_inclusi=p.camera.servizi_inclusi
        ),
        ospite=OspiteResponse(
            id=p.ospite.id,
            nome=p.ospite.nome,
            cognome=p.ospite.cognome,
            documento=p.ospite.documento,
            nazionalita=p.ospite.nazionalita,
            email=p.ospite.email,
            telefono=p.ospite.telefono
        )
    ) for p in prenotazioni]

@app.get("/dashboard/occupazione")
def stato_occupazione(db: Session = Depends(get_db)):
    """Ottiene lo stato di occupazione di tutte le camere"""
    oggi = date.today()
    camere = db.query(Camera).all()
    
    stato = []
    for camera in camere:
        prenotazione_attuale = db.query(Prenotazione).filter(
            Prenotazione.camera_id == camera.id,
            Prenotazione.data_check_in <= oggi,
            Prenotazione.data_check_out > oggi,
            Prenotazione.stato == StatoPrenotazione.CHECK_IN_EFFETTUATO
        ).first()
        
        if prenotazione_attuale:
            stato.append({
                "camera": CameraResponse(
                    id=camera.id,
                    numero=camera.numero,
                    tipo=camera.tipo.value,
                    piano=camera.piano,
                    prezzo_per_notte=camera.prezzo_per_notte,
                    servizi_inclusi=camera.servizi_inclusi
                ),
                "occupata": True,
                "ospite": f"{prenotazione_attuale.ospite.nome} {prenotazione_attuale.ospite.cognome}",
                "check_out_previsto": str(prenotazione_attuale.data_check_out)
            })
        else:
            stato.append({
                "camera": CameraResponse(
                    id=camera.id,
                    numero=camera.numero,
                    tipo=camera.tipo.value,
                    piano=camera.piano,
                    prezzo_per_notte=camera.prezzo_per_notte,
                    servizi_inclusi=camera.servizi_inclusi
                ),
                "occupata": False,
                "ospite": None,
                "check_out_previsto": None
            })
    
    return stato

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)