import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("Profi-Scanner gestartet: Analysiere Layouts und Textstrukturen aus 'aldi.pdf'...")
    neue_liste = []
    
    # Wichtigste Signalwörter zur Bereinigung
    daten_filter = ["ab mo", "ab do", "ab fr", "sa", "fr", "do", "mo", "di", "mi", "woche", "gültig", "vom", "bis", "prospekt"]

    try:
        # pdfplumber öffnet die Datei präzise nach Layout-Blöcken
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Prospektseiten erfolgreich im Speicher analysiert.")
            
            for page_idx, page in enumerate(pdf.pages):
                # .extract_text() von pdfplumber versucht das visuelle Layout (Spalten) beizubehalten
                text = page.extract_text()
                if not text: 
                    continue
                
                zeilen = text.split("\n")
                
                for i, zeile in enumerate(zeilen):
                    zeile_clean = zeile.strip()
                    
                    # 1. Regex sucht flexibel nach Preisen (z.B. 1,49, 1.49, 14.99, optional mit €)
                    preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeile_clean)
                    if preis_treffer:
                        preis_raw = preis_treffer.group(1)
                        
                        # Fallback-Namen vorbereiten aus derselben Zeile
                        roher_name = zeile_clean.replace(preis_raw, "").replace("€", "").strip()
                        
                        # 2. DETEKTOR-TRICK: Wir prüfen die aktuelle Zeile und die oberen Zeilen
                        produkt_name = ""
                        
                        # Wir schauen bis zu 3 Zeilen nach oben, um den echten Namen über dem Preis zu finden
                        for schritt in range(1, 4):
                            if i - schritt >= 0:
                                potentielle_zeile = zeilen[i - schritt].strip()
                                t_check = potentielle_zeile.lower()
                                
                                # Wenn die obere Zeile keinen Preis hat und kein Datum ist, ist es unser Name!
                                if potentielle_zeile and not re.search(r'\d+[\.,]\d{2}', potentielle_zeile):
                                    if not any(wort in t_check for wort in daten_filter):
                                        # Nur sauberen Text behalten, aber wichtige Zeichen erlauben
                                        produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', potentielle_zeile).strip()
                                        break
                        
                        # Wenn oben nichts gefunden wurde, nehmen wir den bereinigten Rest der aktuellen Zeile
                        if not produkt_name or len(produkt_name) < 3:
                            t_check_raw = roher_name.lower()
                            if not any(wort in t_check_raw for wort in daten_filter):
                                produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', roher_name).strip()
                        
                        # Letzter Check: Wenn es immer noch leer oder ein Datum ist, überspringen
                        if not produkt_name or len(produkt_name) < 3 or any(wort in produkt_name.lower() for wort in daten_filter):
                            continue
                        
                        # 3. Blockadefreie Smiley-Zuweisung (Bild-Key)
                        t = produkt_name.lower()
                        key = "apple" if any(w in t for w in ["apfel", "äpfel", "obst"]) \
                            else "potato" if "kartoffel" in t \
                            else "fish" if any(w in t for w in ["lachs", "fisch", "garnelen"]) \
                            else "milkshake" if any(w in t for w in ["paulaner", "spezi", "limo", "getränk", "saft", "cola", "wasser", "bier", "wein", "milch"]) \
                            else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "keks", "bonbon", "haribo", "milka", "eis", "nutella"]) \
                            else "clothes" if any(w in t for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "strick", "jeans", "pullover", "textil"]) \
                            else "default"
                        
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
        print(f"Fehler beim Scannen: {e}")

    # Fallback, falls gar nichts gelesen werden konnte
    if not neue_liste:
        neue_liste = [{
            "markt_id": "aldi", 
            "markt_name": "ALDI SÜD", 
            "produkt_name": "Warte auf PDF-Korrektur", 
            "preis": "0,00 €", 
            "alter_preis": "", 
            "rabatt": "", 
            "gueltigkeit": "KW 42", 
            "bild": "default"
        }]

    # Ergebnis wegschreiben
    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
