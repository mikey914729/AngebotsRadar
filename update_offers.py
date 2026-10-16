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
        pfad = f"daten_{markt}.json"
        if os.path.exists(pfad):
            try:
                with open(pfad, "r", encoding="utf-8") as f:
                    markt_daten = json.load(f)
                    # Verhindert das Hinzufügen von leeren Fallback-Dummys
                    if markt_daten and markt_daten[0].get("produkt_name") != "Warte auf PDF-Korrektur":
                        gesamt_liste.extend(markt_daten)
                        print(f"-> {pfad} erfolgreich zusammengeführt.")
            except Exception as e:
                print(f"⚠️ Fehler beim Lesen von {pfad}: {e}")
        else:
            print(f"ℹ️ {pfad} existiert noch nicht. Überspringe...")

    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(gesamt_liste, f, ensure_ascii=False, indent=2)

    print("=== PIPELINE BEENDET ===")

if __name__ == "__main__":
    master_scraper()
