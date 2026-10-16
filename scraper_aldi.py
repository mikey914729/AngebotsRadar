import json
import re
from pypdf import PdfReader

def aldi_pdf_scanner():
    print("KI-Scanner gestartet: Analysiere die Datei 'aldi.pdf'...")
    neue_liste = []
    
    try:
        # Öffnet die von Ihnen hochgeladene PDF-Datei
        reader = PdfReader("aldi.pdf")
        print(f"-> Prospekt erfolgreich geladen ({len(reader.pages)} Seiten identifiziert).")
        
        # Der Roboter liest Seite für Seite das gesamte Heft durch
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text: continue
            
            # Trennt den Text in einzelne Zeilen
            zeilen = text.split("\n")
            for zeile in zeilen:
                zeile = zeile.strip()
                
                # SPRECH- UND PREISFINDER: Sucht nach Zahlen mit Komma/Punkt und Eurozeichen
                preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeile)
                if preis_treffer:
                    preis_raw = preis_treffer.group(1)
                    
                    # Wir säubern die Zeile, um den Produktnamen herauszufiltern
                    produkt_name = zeile.replace(preis_raw, "").replace("€", "").strip()
                    # Sonderzeichen entfernen
                    produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', produkt_name).strip()
                    
                    # Ein gültiges Produkt braucht einen Namen mit mindestens 4 Buchstaben
                    if len(produkt_name) < 4: continue
                    
                    t = produkt_name.lower()
                    # Automatische Smiley-Zuweisung basierend auf dem gefundenen PDF-Text
                    key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "milkshake" if any(w in t for w in ["paulaner", "spezi", "limo", "getränk", "saft", "cola", "wasser", "bier"]) else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "keks", "bonbon", "haribo", "milka"]) else "clothes" if any(w in t for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "strick", "jeans", "pullover"]) else "default"
                    
                    neue_liste.append({
                        "markt_id": "aldi",
                        "markt_name": "ALDI SÜD",
                        "produkt_name": produkt_name,
                        "preis": f"{preis_raw.replace('.', ',')} €",
                        "alter_preis": "", # Kann bei Bedarf erweitert werden
                        "rabatt": "🔥 PROSPEKT-DEAL",
                        "gueltigkeit": "Aus dem aktuellen PDF",
                        "bild": key
                    })
                    
        print(f"-> Erfolg! Der Scanner hat {len(neue_liste)} Angebote vollautomatisch aus dem PDF extrahiert!")
        
    except FileNotFoundError:
        print("⚠️ Hinweis: Die Datei 'aldi.pdf' wurde noch nicht im Hauptordner hochgeladen.")
    except Exception as e:
        print(f"Fehler beim Scannen des PDFs: {e}")

    # Sicherheitsnetz, falls das PDF komplett leer oder unlesbar verschlüsselt ist
    if not neue_liste:
        neue_liste = [
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "PDF Wartungs-Modus aktiv", "preis": "0,00 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Warte auf Upload", "bild": "default"}
        ]

    # Schreibt die gescannten Daten in den ALDI-Korb
    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_scanner()
