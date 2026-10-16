import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: REINIGUNGS-SCANNER V6 ===")
    neue_liste = []
    
    # Erweiterte, aggressive Blacklist
    blacklist = [
        "kg-preis", "best-preis", "stückpreis", "grundpreis", "je stück", "je kg", 
        "preis", "aktion", "kühlung", "gutes für alle", "klasse", "stg", "packung",
        "becher", "flasche", "z b", "bzw", "ab mo", "ab do", "ab fr", "gültig", 
        "grusel-fans", "mehr auf", "prospekt", "billiger", "sparen", "tiefpreis", "l-preis",
        "top-deals", "für kleine", "deals", "sparpotenzial", "rabatt", "kracher"
    ]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Seiten werden analysiert...")
            
            for page in pdf.pages:
                words = page.extract_words()
                if not words: continue
                
                zeilen_dict = {}
                for w in words:
                    y_pos = int(round(w["top"]))
                    gefunden = False
                    for existing_y in zeilen_dict.keys():
                        if abs(existing_y - y_pos) <= 4:
                            zeilen_dict[existing_y].append(w)
                            gefunden = True
                            break
                    if not gefunden:
                        zeilen_dict[y_pos] = [w]
                
                sortierte_hoehen = sorted(zeilen_dict.keys())
                
                for idx, y in enumerate(sortierte_hoehen):
                    wort_liste = sorted(zeilen_dict[y], key=lambda k: k["x0"])
                    zeilen_text = " ".join([w["text"] for w in wort_liste])
                    
                    alle_preise = re.findall(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    if alle_preise:
                        neuer_preis_raw = alle_preise[-1]
                        alter_preis_raw = alle_preise[0] if len(alle_preise) > 1 else ""
                        
                        produkt_name = ""
                        
                        # Bis zu 5 Zeilen hochwandern
                        for schritt in range(1, 6):
                            if idx - schritt >= 0:
                                obere_y = sortierte_hoehen[idx - schritt]
                                obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                                obere_zeile_text = " ".join([w["text"] for w in obere_woerter]).strip()
                                
                                # Alten Preis oben drüber abfangen
                                obere_preise = re.findall(r'(\d+[\.,]\d{2})\s*€?', obere_zeile_text)
                                if obere_preise and not alter_preis_raw:
                                    alter_preis_raw = obere_preise[0]
                                
                                if obere_zeile_text and not re.search(r'\d+[\.,]\d{2}', obere_zeile_text):
                                    # Radikaler Check: Keine Füllwörter und keine reinen Nummern/Prozentzeichen/Minuszeichen
                                    if not any(b in obere_zeile_text.lower() for b in blacklist):
                                        if not re.search(r'[-+%33]', obere_zeile_text): # Blockiert explizit "-33"
                                            if len(obere_zeile_text.strip()) > 3:
                                                produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', obere_zeile_text).strip()
                                                break
                        
                        # Fallback
                        if not produkt_name or len(produkt_name) < 3:
                            roher_rest = zeilen_text
                            for pr in alle_preise:
                                roher_rest = roher_rest.replace(pr, "")
                            roher_rest = roher_rest.replace("€", "").strip()
                            
                            if not any(b in roher_rest.lower() for b in blacklist):
                                if not re.search(r'[-+%33]', roher_rest):
                                    if len(roher_rest) > 3:
                                        produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', roher_rest).strip()
                        
                        # Letzte harte Filterbarriere vor dem Speicher
                        if not produkt_name or len(produkt_name) < 3 or any(b in produkt_name.lower() for b in blacklist):
                            continue
                        if re.search(r'[-+%33]', produkt_name):
                            continue
                        
                        preis_final = f"{neuer_preis_raw.replace('.', ',')} €"
                        alter_preis_final = f"{alter_preis_raw.replace('.', ',')} €" if alter_preis_raw else ""
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": produkt_name,
                            "preis": preis_final,
                            "alter_preis": alter_preis_final,
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": "default"
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} ECHTE Produkte ===")
    except Exception as e:
        print(f"Fehler: {e}")

    # Hier leeren wir die JSON absichtlich NICHT mehr mit Müll-Dummys
    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
