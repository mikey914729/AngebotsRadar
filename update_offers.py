import json
import subprocess

def master_scraper():
    print("=== STARTE MULTI-MARKT-PIPELINE ===")
    
    # KORREKTUR: Alle 7 Märkte sind jetzt lückenlos eingepflegt!
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
            print(f"⚠️ Warnung: {skript} meldet eine Störung: {e}. Überspringe Markt...")

    print("=== PIPELINE ERFOLGREICH BEENDET! ===")

if __name__ == "__main__":
    master_scraper()
