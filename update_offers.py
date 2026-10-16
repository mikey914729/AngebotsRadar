import json
import subprocess

def master_scraper():
    print("=== STARTE REPARIERTE MULTI-MARKT-PIPELINE ===")
    
    # 1. Alle Skripte nacheinander ausführen
    skripte = [
        "scraper_aldi.py",
        "scraper_penny.py",
        "scraper_edeka.py",
        "scraper_netto.py",
        "scraper_rossmann.py",
        "scraper_fressnapf.py",
        "scraper_baumarkt.py"
    ]
    
    for skript in skripte:
        try:
            print(f"Starte Teilsystem: {skript}...")
            subprocess.run(["python", skript], check=True)
        except Exception as e:
            print(f"⚠️ Störung bei {skript}: {e}. Nutze bestehende Daten für diesen Markt.")

    # 2. DER ZUSAMMENFÜHRUNGS-TRICK: Der Chef sammelt alle Körbe ein
    gesamt_liste = []
    maerkte = ["aldi", "penny", "edeka", "netto", "rossmann", "fressnapf", "baumarkt"]
    
    for markt in maerkte:
        try:
            with open(f"daten_{markt}.json", "r", encoding="utf-8") as f:
                markt_daten = json.load(f)
                gesamt_liste.extend(markt_daten)
                print(f"-> {markt.upper()}: {len(markt_daten)} Angebote hinzugefügt.")
        except:
            print(f"-> {markt.upper()}: Korb leer oder temporär nicht erreichbar.")

    # 3. Ein einziges Mal final in die daten.json schreiben
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(gesamt_liste, f, ensure_ascii=False, indent=2)

    print(f"=== PIPELINE BEREINIGT: {len(gesamt_liste)} ANGEBOTE GESICHERT ===")

if __name__ == "__main__":
    master_scraper()
