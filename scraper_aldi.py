import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: KOORDINATEN-SCANNER V3 ===")
    neue_liste = []
    
    # Werbe-Wörter und Grundpreise fliegen hier rigoros raus
    blacklist = [
        "kg-preis", "best-preis", "stückpreis", "grundpreis", "je stück", "je kg", 
        "preis", "aktion", "kühlung", "gutes für alle", "klasse", "stg", "packung",
        "becher", "flasche", "z b", "bzw", "ab mo", "ab do", "ab fr", "gültig", 
        "grusel-fans", "mehr auf", "prospekt", "billiger", "sparen", "tiefpreis", "l-preis"
    ]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Seiten werden analysiert...")
            
            for page in pdf.pages:
                words = page.extract_words()
                if not words: 
                    continue
                
                # Wörter nach Höhen-Koordinaten sortieren (Zeilen bauen)
                zeilen_dict = {}
                for w in words:
                    y_pos = int(round(w["top"]))
                    gefunden = False
                    for existing_y in zeilen_dict.keys():
                        if abs(existing_y - y_pos) <= 4: # 4 Pixel Toleranz
                            zeilen_dict[existing_y].append(w)
                            gefunden = True
                            break
                    if not gefunden:
                        zeilen_dict[y_pos] = [w]
                
                sortierte_hoehen = sorted(zeilen_dict.keys())
                
                for idx, y in enumerate(sortierte_hoehen):
                    wort_liste = sorted(zeilen_dict[y], key=lambda k: k["x0"])
                    zeilen_text = " ".join([w["text"] for w in wort_liste])
                    
                    # Such nach Preisen (z.B. 4,99)
                    preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    if preis_treffer:
                        preis_raw = preis_treffer.group(1)
                        produkt_name = ""
                        
                        # Suche in den Zeilen DIREKT DARÜBER nach dem Namen
                        for schritt in range(1, 5):
                            if idx - schritt >= 0:
                                obere_y = sortierte_hoehen[idx - schritt]
                                obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                                obere_zeile_text = " ".join([w["text"] for w in obere_woerter]).strip()
                                
                                if obere_zeile_text and not re.search(r'\d+[\.,]\d{2}', obere_zeile_text):
                                    # HIER IST DER SCHUTZ: Wenn Blacklist-Wort drin ist, ignorieren!
                                    if not any(b in obere_zeile_text.lower() for b in blacklist):
                                        produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', obere_zeile_text).strip()
                                        break
                        
                        # Fallback: Dieselbe Zeile links neben dem Preis
                        if not produkt_name or len(produkt_name) < 3:
                            roher_rest = zeilen_text.replace(preis_raw, "").replace("€", "").strip()
                            if not any(b in roher_rest.lower() for b in blacklist):
                                produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', roher_rest).strip()
                        
                        # Radikale Endkontrolle: Ist der Name Müll oder zu kurz? Weg damit!
                        if not produkt_name or len(produkt_name) < 3 or any(b in produkt_name.lower() for b in blacklist):
                            continue
                        
                        # Smiley-Zuweisung
                        t = produkt_name.lower()
                        key = "apple" if any(w in t for w in ["apfel", "äpfel", "obst", "banane"]) \
                            else "potato" if "kartoffel" in t \
                            else "fish" if any(w in t for w in ["lachs", "fisch"]) \
                            else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "haribo"]) \
                            else "milkshake" if any(w in t for w in ["spezi", "cola", "wasser", "bier", "saft"]) \
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
                        
        print(f"=== ENDE: {len(neue_liste)} ECHTE Produkte gefunden ===")
    except Exception as e:
        print(f"Fehler: {e}")

    if not neue_liste:
        neue_liste = [{"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Warte auf PDF-Korrektur", "preis": "0,00 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "KW 42", "bild": "default"}]

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
