import json
import os

# Direktes Importieren der Markt-Scanner-Funktionen
# (Stelle sicher, dass die Funktionen in den jeweiligen Skripten so heißen!)
try: from scraper_aldi import aldi_pdf_profi_scanner
except: aldi_pdf_profi_scanner = None

def master_scraper():
    print("=== STARTE MULTI-MARKT-PIPELINE (NATIV) ===")
    
    # 1. ALDI SÜD direkt ausführen (Ohne unsicheres subprocess)
    if aldi_pdf_profi_scanner:
        try:
            print("Starte Teilsystem: scraper_aldi.py (Direktimport)...")
            aldi_pdf_profi_scanner()
        except Exception as e:
            print(f"⚠️ Störung bei scraper_aldi.py: {e}")
    else:
        print("Starte Teilsystem: scraper_aldi.py via Fallback...")
        os.system("python3 scraper_aldi.py")

    # 2. ALLE ANDEREN SKRIPTE HIER HINTEREINANDER AUSFÜHREN
    # Wir nutzen "python3", da "python" auf GitHub Actions oft fehlschlägt!
    restliche_skripte = [
        "scraper_penny.py",
        "scraper_edeka.py",
        "scraper_netto.py",
        "scraper_rossmann.py",
        "scraper_fressnapf.py",
        "scraper_baumarkt.py"
    ]
    
    for skript in restliche_skripte:
        try:
            print(f"Starte Teilsystem: {skript}...")
            # Umstieg auf os.system mit python3 für maximale Stabilität auf Linux/GitHub
            os.system(f"python3 {skript}")
        except Exception as e:
            print(f"⚠️ Störung bei {skript}: {e}")

        # Zusammenführung aller Körbe in die daten.json
    gesamt_liste = []
    maerkte = ["aldi", "penny", "edeka", "netto", "rossmann", "fressnapf", "baumarkt"]
    
    for markt in maerkte:
        try:
            # Wir zwingen das System, jede Datei einzeln zu lesen, selbst wenn andere fehlen!
            with open(f"daten_{markt}.json", "r", encoding="utf-8") as f:
                markt_daten = json.load(f)
                gesamt_liste.extend(markt_daten)
                print(f"Erfolgreich geladen: daten_{markt}.json")
        except Exception as e:
            print(f"Hinweis: daten_{markt}.json konnte nicht geladen werden, überspringe... ({e})")

        else:
            print(f"ℹ️ {pfad} existiert noch nicht. Überspringe...")

    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(gesamt_liste, f, ensure_ascii=False, indent=2)

    print("=== PIPELINE BEENDET ===")

if __name__ == "__main__":
    master_scraper()
