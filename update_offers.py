import json
import os
import subprocess

def master_scraper():
    print("=== STARTE MULTI-MARKT-PIPELINE (SICHERHEITS-MODUS) ===")
    
    # Liste aller Skripte
    skripte = [
        "scraper_aldi.py",
        "scraper_penny.py",
        "scraper_edeka.py",
        "scraper_netto.py",
        "scraper_rossmann.py",
        "scraper_fressnapf.py",
        "scraper_baumarkt.py"
    ]
    
    # Jedes Skript wird isoliert gestartet. Stürzt eines ab, läuft die Pipeline trotzdem weiter!
    for skript in skripte:
        if os.path.exists(skript):
            try:
                print(f"Starte Teilsystem: {skript}...")
                # Führt das Skript explizit mit python3 aus und wartet auf das Ende
                subprocess.run(["python3", skript], check=True)
                print(f"-> {skript} erfolgreich beendet.")
            except Exception as e:
                print(f"⚠️ Störung bei {skript}, System läuft weiter: {e}")
        else:
            print(f"ℹ️ Skript {skript} nicht gefunden. Überspringe...")

    print("=== ZUSAMMENFÜHRUNG DER DATEN ===")
    gesamt_liste = []
    maerkte = ["aldi", "penny", "edeka", "netto", "rossmann", "fressnapf", "baumarkt"]
    
    for markt in maerkte:
        pfad = f"daten_{markt}.json"
        if os.path.exists(pfad):
            try:
                with open(pfad, "r", encoding="utf-8") as f:
                    markt_daten = json.load(f)
                    if isinstance(markt_daten, list) and len(markt_daten) > 0:
                        # Verhindert das Hinzufügen von fehlerhaften Dummy-Einträgen
                        if markt_daten[0].get("produkt_name") != "Warte auf PDF-Korrektur":
                            gesamt_liste.extend(markt_daten)
                            print(f"-> {pfad} ({len(markt_daten)} Produkte) hinzugefügt.")
            except Exception as e:
                print(f"⚠️ Fehler beim Einlesen von {pfad}: {e}")
        else:
            print(f"ℹ️ {pfad} fehlt. Keine Daten für diesen Markt.")

    # Schreibt die endgültige Datei für deine Webseite
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(gesamt_liste, f, ensure_ascii=False, indent=2)

    print("=== PIPELINE BEENDET ===")

if __name__ == "__main__":
    master_scraper()
