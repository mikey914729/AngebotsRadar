import json
import re
from pypdf import PdfReader

def aldi_pdf_profi_scanner():
    print("Profi-Scanner gestartet: Bereinige Textstrukturen aus 'aldi.pdf'...")
    neue_liste = []
    
    try:
        reader = PdfReader("aldi.pdf")
        print(f"-> {len(reader.pages)} Prospektseiten erfolgreich im Speicher analysiert.")
        
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text: continue
            
            zeilen = text.split("\n")
            for i, zeile in enumerate(zeilen):
                zeile = zeile.strip()
                
                # Sucht nach Preisen mit Komma oder Punkt
                preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeile)
                if preis_treffer:
                    preis_raw = preis_treffer.group(1)
                    
                    # Wir holen uns den potenziellen Produktnamen aus dieser Zeile
                    roher_name = zeile.replace(preis_raw, "").replace("€", "").strip()
                    roher_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', roher_name).strip()
                    
                    # DETEKTOR-TRICK: Wenn der gefundene Name ein Datum oder Wochentag ist,
                    # schauen wir stattdessen 1 oder 2 Zeilen HÖHER im PDF nach dem echten Namen!
                    t_check = roher_name.lower()
                    ist_datum = any(w in t_check for w in ["ab mo", "ab do", "ab fr", "sa", "fr", "do", "mo", "di", "mi", "woche", "gültig", "vom", "bis", "1610", "1710", "1510"])
                    
                    if ist_datum or len(roher_name) < 4:
                        # Rettungs-Schleife: Wir wandern im Text nach oben, um den echten Namen zu greifen
                        for standard_index in range(1, 3):
                            if i - standard_index >= 0:
                                check_zeile = zeilen[i - standard_index].strip()
                                check_zeile = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', check_zeile).strip()
                                # Wenn die obere Zeile keinen Preis und kein Datum enthält, ist es unser Produktname!
                                if check_zeile and not re.search(r'\d+[\.,]\d{2}', check_zeile) and not any(w in check_zeile.lower() for w in ["ab mo", "ab do", "ab fr", "sa", "1710"]):
                                    roher_name = check_zeile
                                    break
                    
                    # Bereinigung des finalen Produktnamens
                    produkt_name = roher_name.strip()
                    if len(produkt_name) < 4 or any(w in produkt_name.lower() for w in ["ab mo", "ab do", "1710"]): 
                        continue # Wenn immer noch Müll, überspringen
                    
                    t = produkt_name.lower()
                    # Blockadefreie Smiley-Zuweisung für die bereinigten Produkte
                    key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "milkshake" if any(w in t for w in ["paulaner", "spezi", "limo", "getränk", "saft", "cola", "wasser", "bier"]) else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "keks", "bonbon", "haribo", "milka"]) else "clothes" if any(w in t for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "strick", "jeans", "pullover"]) else "default"
                    
                    neue_liste.append({
                        "markt_id": "aldi",
                        "markt_name": "ALDI SÜD",
                        "produkt_name": produkt_name,
                        "preis": f"{preis_raw.replace('.', ',')} €",
                        "alter_preis": "",
                        "rabatt": "🔥 PROSPEKT-DEAL",
                        "gueltigkeit": "KW 42",
                        "bild": key
                    })
                    
        print(f"-> Bereinigung beendet: {len(neue_liste)} ECHTE Produkte erfolgreich gefiltert!")
        
    except Exception as e:
        print(f"Fehler: {e}")

    if not neue_liste:
        neue_liste = [{"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Warte auf PDF-Korrektur", "preis": "0,00 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "KW 42", "bild": "default"}]

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
