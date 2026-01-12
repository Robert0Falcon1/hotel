"""
Popolamento database con dati di esempio
"""
from datetime import datetime, timedelta, date
import random
from backend.database import SessionLocal
from backend.models import Camera, Ospite, Prenotazione, TipoCamera, StatoPrenotazione


def seed_database():
    """Popola il database con dati di esempio"""
    session = SessionLocal()
    
    try:
        # Verifica se ci sono già dati
        if session.query(Camera).count() > 0:
            print("⚠️  Database già popolato, skip seed data")
            return
        
        print("📊 Popolamento database in corso...")
        
        # Crea camere
        camere = [
            Camera(numero="101", tipo=TipoCamera.SINGOLA, piano=1, prezzo_per_notte=80,
                   servizi_inclusi="WiFi, TV, Aria condizionata"),
            Camera(numero="102", tipo=TipoCamera.SINGOLA, piano=1, prezzo_per_notte=80,
                   servizi_inclusi="WiFi, TV, Aria condizionata"),
            Camera(numero="103", tipo=TipoCamera.SINGOLA, piano=1, prezzo_per_notte=85,
                   servizi_inclusi="WiFi, TV, Aria condizionata, Scrivania"),
            Camera(numero="201", tipo=TipoCamera.DOPPIA, piano=2, prezzo_per_notte=120,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata"),
            Camera(numero="202", tipo=TipoCamera.DOPPIA, piano=2, prezzo_per_notte=120,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata"),
            Camera(numero="203", tipo=TipoCamera.DOPPIA, piano=2, prezzo_per_notte=130,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata, Vista mare"),
            Camera(numero="204", tipo=TipoCamera.DOPPIA, piano=2, prezzo_per_notte=135,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata, Vista mare, Balcone"),
            Camera(numero="301", tipo=TipoCamera.SUITE, piano=3, prezzo_per_notte=200,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata, Jacuzzi, Vista panoramica"),
            Camera(numero="302", tipo=TipoCamera.SUITE, piano=3, prezzo_per_notte=220,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata, Jacuzzi, Balcone, Vista mare"),
            Camera(numero="303", tipo=TipoCamera.SUITE, piano=3, prezzo_per_notte=250,
                   servizi_inclusi="WiFi, TV, Minibar, Aria condizionata, Jacuzzi, Balcone, Vista mare, Sala living"),
        ]
        session.add_all(camere)
        session.flush()
        print(f"✅ Aggiunte {len(camere)} camere")
        
        # Crea ospiti
        ospiti = [
            Ospite(nome="Mario", cognome="Rossi", documento="AB123456",
                   nazionalita="Italiana", email="mario.rossi@email.it", telefono="+39 333 1234567"),
            Ospite(nome="Laura", cognome="Bianchi", documento="CD789012",
                   nazionalita="Italiana", email="laura.bianchi@email.it", telefono="+39 345 7890123"),
            Ospite(nome="Giuseppe", cognome="Verdi", documento="EF345678",
                   nazionalita="Italiana", email="giuseppe.verdi@email.it", telefono="+39 348 5551234"),
            Ospite(nome="John", cognome="Smith", documento="US456789",
                   nazionalita="Americana", email="john.smith@email.com", telefono="+1 555 1234567"),
            Ospite(nome="Sophie", cognome="Dupont", documento="FR789123",
                   nazionalita="Francese", email="sophie.dupont@email.fr", telefono="+33 6 12345678"),
            Ospite(nome="Hans", cognome="Mueller", documento="DE555888",
                   nazionalita="Tedesca", email="hans.mueller@email.de", telefono="+49 176 12345678"),
            Ospite(nome="Maria", cognome="Garcia", documento="ES777999",
                   nazionalita="Spagnola", email="maria.garcia@email.es", telefono="+34 666 123456"),
        ]
        session.add_all(ospiti)
        session.flush()
        print(f"✅ Aggiunti {len(ospiti)} ospiti")
        
        # Crea prenotazioni (ultimi 5 mesi)
        oggi = date.today()
        prenotazioni = []
        
        # Prenotazioni passate completate (ultimi 5 mesi)
        for i in range(20):
            giorni_fa = random.randint(30, 150)
            check_in = oggi - timedelta(days=giorni_fa)
            durata = random.randint(2, 7)
            check_out = check_in + timedelta(days=durata)
            camera = random.choice(camere)
            ospite = random.choice(ospiti)
            prezzo = camera.prezzo_per_notte * durata
            
            prenotazioni.append(Prenotazione(
                camera_id=camera.id,
                ospite_id=ospite.id,
                data_check_in=check_in,
                data_check_out=check_out,
                numero_ospiti=random.randint(1, 2),
                prezzo_totale=prezzo,
                stato=StatoPrenotazione.CHECK_OUT_COMPLETATO
            ))
        
        # Prenotazioni attuali (check-in effettuato)
        for i in range(4):
            giorni_fa = random.randint(0, 3)
            check_in = oggi - timedelta(days=giorni_fa)
            durata = random.randint(3, 7)
            check_out = check_in + timedelta(days=durata)
            camera = camere[i]
            ospite = ospiti[i]
            prezzo = camera.prezzo_per_notte * durata
            
            prenotazioni.append(Prenotazione(
                camera_id=camera.id,
                ospite_id=ospite.id,
                data_check_in=check_in,
                data_check_out=check_out,
                numero_ospiti=random.randint(1, 2),
                prezzo_totale=prezzo,
                stato=StatoPrenotazione.CHECK_IN_EFFETTUATO
            ))
        
        # Prenotazioni future confermate
        for i in range(8):
            giorni_futuro = random.randint(1, 60)
            check_in = oggi + timedelta(days=giorni_futuro)
            durata = random.randint(2, 5)
            check_out = check_in + timedelta(days=durata)
            camera = random.choice(camere)
            ospite = random.choice(ospiti)
            prezzo = camera.prezzo_per_notte * durata
            
            prenotazioni.append(Prenotazione(
                camera_id=camera.id,
                ospite_id=ospite.id,
                data_check_in=check_in,
                data_check_out=check_out,
                numero_ospiti=random.randint(1, 2),
                prezzo_totale=prezzo,
                stato=StatoPrenotazione.CONFERMATA
            ))
        
        session.add_all(prenotazioni)
        session.commit()
        print(f"✅ Aggiunte {len(prenotazioni)} prenotazioni")
        print("🎉 Database popolato con successo!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Errore durante il popolamento: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    from backend.database import init_database
    init_database()
    seed_database()