import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: REINIGUNGS-SCANNER V12 (UNIVERSAL) ===")
    neue_liste = []
    
    # Begriffe, die wir aus dem Namen herausfiltern
    muell_woerter = [
        "l-preis", "l-flasche", "ml-flasche", "flasche", "vol", "sorten", "frankreich",
        "italien", "deutschland", "kg-preis", "best-preis", "stückpreis", "grundpreis", 
        "je stück", "je kg", "aktion", "ab mo", "ab do", "sparpotenzial", "dauerhaft", "die preise"
    ]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Seiten werden analysiert...")
            
            for page in pdf.pages:
                words = page.extract_words()
                if not words: continue
                
                # Zeilen basierend auf den Höhen-Koordinaten bauen
                zeilen_dict = {}
                for w in words:
                    y_pos = int(round(w["top"]))
                    gefunden = False
                    for existing_y in zeilen_dict.keys():
                        if abs(existing_y - y_pos) <= 5: # 5 Pixel Toleranz
                            zeilen_dict[existing_y].append(w)
                            gefunden = True
                            break
                    if not gefunden:
                        zeilen_dict[y_pos] = [w]
                
                sortierte_hoehen = sorted(zeilen_dict.keys())
                
                for idx, y in enumerate(sortierte_hoehen):
                    wort_liste = sorted(zeilen_dict[y], key=lambda k: k["x0"])
                    zeilen_text = " ".join([w["text"] for w in wort_liste])
                    
                    # FEHLERTOLERANTER REGEX: Findet Preise mit Punkt ODER Komma, optional mit €
                    preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    if preis_treffer:
                        preis_raw = preis_treffer.group(1)
                        
                        # Wir holen uns den restlichen Text der Zeile als Produktnamen
                        roher_name = zeilen_text.replace(preis_raw, "").replace("€", "").strip()
                        
                        # Falls die Zeile leer ist, schauen wir kurz eine Zeile höher nach
                        if len(roher_name) < 3 and idx - 1 >= 0:
                            obere_y = sortierte_hoehen[idx - 1]
                            obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                            roher_name = " ".join([w["text"] for w in obere_woerter]).strip()
                        
                        # BEREINIGUNG: Müllwörter löschen
                        name_clean = roher_name
                        for mw in muell_woerter:
                            name_clean = re.sub(re.escape(mw), "", name_clean, flags=re.IGNORECASE)
                        
                        # Reine Nummernkolonnen (3- oder 4-stellig wie 2399, 713) löschen
                        name_clean = re.sub(r'\b\d{3,4}\b', "", name_clean)
                        
                        # Sonderzeichen entfernen und Text glätten
                        name_clean = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', name_clean)
                        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
                        
                        # Wenn fast nichts übrig bleibt, setzen wir einen soliden Platzhalter statt abzubrechen
                        if len(name_clean) < 2:
                            name_clean = "ALDI Aktionsartikel"
                        
                        t_lower = name_clean.lower()
                        key = "apple" if "apfel" in t_lower else "fish" if "fisch" in t_lower else "chocolate" if "schoko" in t_lower else "default"
                        
                        # Preis einheitlich mit Komma formatieren
                        preis_final = f"{preis_raw.replace('.', ',')} €"
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": name_clean,
                            "preis": preis_final,
                            "alter_preis": "",
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} Produkte erfolgreich importiert ===")
    except Exception as e:
        print(f"Fehler: {e}")

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
