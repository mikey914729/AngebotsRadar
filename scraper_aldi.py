import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("Profi-Scanner gestartet: Analysiere Objekt-Koordinaten aus 'aldi.pdf'...")
    neue_liste = []
    
    # Rigerose Blacklist für Wörter, die NIEMALS ein Produktname sein dürfen
    blacklist = [
        "kg-preis", "best-preis", "stückpreis", "grundpreis", "je stück", "je kg", 
        "preis", "aktion", "kühlung", "gutes für alle", "klasse", "stg", "packung",
        "becher", "flasche", "z b", "bzw", "ab mo", "ab do", "ab fr", "gültig", 
        "grusel-fans", "mehr auf", "prospekt", "billiger", "sparen", "tiefpreis"
    ]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Prospektseiten erfolgreich im Speicher analysiert.")
            
            for page_idx, page in enumerate(pdf.pages):
                # Wir holen uns alle Wörter mit ihren exakten Pixel-Koordinaten
                words = page.extract_words()
                if not words: 
                    continue
                
                # Wir bauen zuerst saubere Zeilen basierend auf den exakten Höhen-Koordinaten (top) auf
                # Das verhindert das seitliche Zusammenrutschen von verschiedenen Spalten!
                zeilen_dict = {}
                for w in words:
                    # Runden auf ganze Zahlen, damit Wörter auf minimal versetzter Höhe in derselben Zeile landen
                    y_pos = int(round(w["top"]))
                    
                    # Toleranzbereich von 3 Pixeln für eine gemeinsame Zeile gewähren
                    gefunden = False
                    for existing_y in zeilen_dict.keys():
                        if abs(existing_y - y_pos) <= 3:
                            zeilen_dict[existing_y].append(w)
                            gefunden = True
                            break
                    if not gefunden:
                        zeilen_dict[y_pos] = [w]
                
                # Sortiere die Zeilen von oben nach unten
                sortierte_hoehen = sorted(zeilen_dict.keys())
                
                for idx, y in enumerate(sortierte_hoehen):
                    # Sortiere die Wörter innerhalb einer Zeile strikt von links nach rechts (x0)
                    wort_liste = sorted(zeilen_dict[y], key=lambda k: k["x0"])
                    zeilen_text = " ".join([w["text"] for w in wort_liste])
                    
                    # 1. Such nach einem gültigen Preis in dieser Zeile
                    preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    if preis_treffer:
                        preis_raw = preis_treffer.group(1)
                        
                        # 2. Produktnamen-Detektor über Koordinaten
                        produkt_name = ""
                        
                        # Strategie A: Wir schauen in den Zeilen DIREKT DARÜBER (bis zu 4 Zeilen nach oben)
                        for schritt in range(1, 5):
                            if idx - schritt >= 0:
                                obere_y = sortierte_hoehen[idx - schritt]
                                obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                                obere_zeile_text = " ".join([w["text"] for w in obere_woerter]).strip()
                                
                                # Säubern von Sonderzeichen für den Check
                                check_text = obere_zeile_text.lower()
                                
                                # Wenn die obere Zeile keinen Preis hat und kein Müll-Wort ist, nehmen wir sie!
                                if obere_zeile_text and not re.search(r'\d+[\.,]\d{2}', obere_zeile_text):
                                    if not any(block in check_text for block in blacklist) and len(obere_zeile_text) > 3:
                                        # Nur erlaubte Zeichen filtern
                                        produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', obere_zeile_text).strip()
                                        break
                        
                        # Strategie B: Fallback auf dieselbe Zeile (falls der Name links neben dem Preis steht)
                        if not produkt_name or len(produkt_name) < 3:
                            roher_rest = zeilen_text.replace(preis_raw, "").replace("€", "").strip()
                            check_rest = roher_rest.lower()
                            if not any(block in check_rest for block in blacklist) and len(roher_rest) > 3:
                                produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', roher_rest).strip()
                        
                        # 3. Validierung: Wenn immer noch ungültig oder auf der Blacklist, komplett überspringen
                        if not produkt_name or len(produkt_name) < 3 or any(block in produkt_name.lower() for block in blacklist):
                            continue
                        
                        # 4. Smiley-Kategorie-Zuweisung basierend auf dem gefundenen Namen
                        t = produkt_name.lower()
                        key = "apple" if any(w in t for w in ["apfel", "äpfel", "obst", "banane", "trauben", "birne"]) \
                            else "potato" if "kartoffel" in t \
                            else "fish" if any(w in t for w in ["lachs", "fisch", "garnelen", "seelachs"]) \
                            else "milkshake" if any(w in t for w in ["paulaner", "spezi", "limo", "getränk", "saft", "cola", "wasser", "bier", "wein", "milch", "saft", "smoothie"]) \
                            else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "keks", "bonbon", "haribo", "milka", "eis", "nutella", "pralinen"]) \
                            else "clothes" if any(w in t for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "strick", "jeans", "pullover", "textil", "kleid"]) \
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
        print(f"Fehler beim Koordinaten-Scan: {e}")

    # Fallback, falls die Liste leer bleibt
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

    # In die daten_aldi.json schreiben
    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
