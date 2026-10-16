import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: REINIGUNGS-SCANNER V13 (FINALE FILTRATION) ===")
    neue_liste = []
    
    # Harte Blacklist für System-Texte, Datumsangaben und Werbeslogans
    blacklist = [
        "kg-preis", "best-preis", "stückpreis", "grundpreis", "je stück", "je kg", 
        "preis", "aktion", "kühlung", "gutes für alle", "klasse", "stg", "packung",
        "becher", "flasche", "z b", "bzw", "ab mo", "ab do", "ab fr", "gültig", 
        "mehr auf", "prospekt", "billiger", "sparen", "tiefpreis", "l-preis",
        "top-deals", "für kleine", "deals", "sparpotenzial", "rabatt", "kracher",
        "von mo", "von do", "von fr", "sa", "fr", "do", "mo", "di", "mi", "woche"
    ]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            print(f"-> {len(pdf.pages)} Seiten werden analysiert...")
            
            for page in pdf.pages:
                words = page.extract_words()
                if not words: continue
                
                # Zeilen basierend auf Höhen-Koordinaten aufbauen
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
                    
                    # Such nach Preisen (Punkt oder Komma)
                    preis_treffer = re.search(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    if preis_treffer:
                        preis_raw = preis_treffer.group(1)
                        
                        # Wir isolieren den Text aus derselben Zeile
                        roher_name = zeilen_text.replace(preis_raw, "").replace("€", "").strip()
                        
                        # INTELLIGENTE WANDER-SCHLEIFE:
                        # Wenn die aktuelle Zeile leer ist oder nur Müll/Datumsangaben enthält,
                        # wandern wir bis zu 4 Zeilen nach OBEN, um den echten Produktnamen zu finden!
                        t_check_raw = roher_name.lower()
                        ist_zeile_muell = any(b in t_check_raw for b in blacklist) or len(roher_name) < 3 or re.match(r'^[-+]?\d+\s*%?$', roher_name.strip())
                        
                        if ist_zeile_muell:
                            for schritt in range(1, 5):
                                if idx - schritt >= 0:
                                    obere_y = sortierte_hoehen[idx - schritt]
                                    obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                                    obere_zeile_text = " ".join([w["text"] for w in obere_woerter]).strip()
                                    
                                    t_check_oben = obere_zeile_text.lower()
                                    # Die obere Zeile darf kein Preis, kein Datum und keine reine Zahl sein
                                    if obere_zeile_text and not re.search(r'\d+[\.,]\d{2}', obere_zeile_text):
                                        if not any(b in t_check_oben for b in blacklist):
                                            if not re.match(r'^[-+]?\d+\s*%?$', obere_zeile_text.strip()):
                                                roher_name = obere_zeile_text
                                                break
                        
                        # Füllwörter und Einheiten direkt aus dem Text löschen
                        name_clean = roher_name
                        for mw in ["l-preis", "l-flasche", "ml-flasche", "flasche", "vol", "sorten", "frankreich", "italien", "deutschland"]:
                            name_clean = re.sub(re.escape(mw), "", name_clean, flags=re.IGNORECASE)
                        
                        # Reine Nummernkolonnen (wie 2399, 713, 219) restlos entfernen
                        name_clean = re.sub(r'\b\d{2,4}\b', "", name_clean)
                        
                        # Sonderzeichen entfernen und Text glätten
                        name_clean = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', name_clean)
                        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
                        
                        # Letzter, knallharter End-Check
                        if len(name_clean) < 3 or any(b in name_clean.lower() for b in blacklist):
                            continue
                        if re.match(r'^[-+]?\d+\s*%?$', name_clean): # Verhindert "-33"
                            continue
                        
                        t_lower = name_clean.lower()
                        key = "apple" if "apfel" in t_lower else "fish" if "fisch" in t_lower else "chocolate" if "schoko" in t_lower else "default"
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": name_clean,
                            "preis": f"{preis_raw.replace('.', ',')} €",
                            "alter_preis": "",
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} ECHTE Produkte sauber extrahiert ===")
    except Exception as e:
        print(f"Fehler: {e}")

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
