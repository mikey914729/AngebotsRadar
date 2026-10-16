import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: PREIS-VERGLEICHS-SCANNER V5 ===")
    neue_liste = []
    
    # Absolute Blacklist für Überschriften und Slogans
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
                if not words: 
                    continue
                
                # Zeilen basierend auf Höhen-Koordinaten clustern
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
                    
                    # Such nach allen Preisen in dieser Zeile
                    alle_preise = re.findall(r'(\d+[\.,]\d{2})\s*€?', zeilen_text)
                    
                    if alle_preise:
                        # Der letzte gefundene Preis in der Preis-Zeile ist meistens der aktuelle, neue Preis
                        neuer_preis_raw = alle_preise[-1]
                        alter_preis_raw = ""
                        
                        # Wenn zwei Preise in derselben Zeile stehen, ist der erste der alte Preis
                        if len(alle_preise) > 1:
                            alter_preis_raw = alle_preise[0]
                        
                        produkt_name = ""
                        
                        # Wir wandern bis zu 5 Zeilen hoch, um den Namen zu finden und nach dem alten Preis zu suchen
                        for schritt in range(1, 6):
                            if idx - schritt >= 0:
                                obere_y = sortierte_hoehen[idx - schritt]
                                obere_woerter = sorted(zeilen_dict[obere_y], key=lambda k: k["x0"])
                                obere_zeile_text = " ".join([w["text"] for w in obere_woerter]).strip()
                                
                                # Falls oben drüber noch ein einzelner Preis steht (oft der alte Streichpreis), sichern wir ihn
                                obere_preise = re.findall(r'(\d+[\.,]\d{2})\s*€?', obere_zeile_text)
                                if obere_preise and not alter_preis_raw:
                                    alter_preis_raw = obere_preise[0]
                                
                                if obere_zeile_text and not re.search(r'\d+[\.,]\d{2}', obere_zeile_text):
                                    if not any(b in obere_zeile_text.lower() for b in blacklist):
                                        if not re.match(r'^[-+]?\d+\s*%?$', obere_zeile_text.strip()):
                                            produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', obere_zeile_text).strip()
                                            break
                        
                        # Fallback auf dieselbe Zeile
                        if not produkt_name or len(produkt_name) < 3:
                            roher_rest = zeilen_text
                            for pr in alle_preise:
                                roher_rest = roher_rest.replace(pr, "")
                            roher_rest = roher_rest.replace("€", "").strip()
                            
                            if not any(b in roher_rest.lower() for b in blacklist):
                                if not re.match(r'^[-+]?\d+\s*%?$', roher_rest.strip()):
                                    produkt_name = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/\.,&]', '', roher_rest).strip()
                        
                        # Radikaler End-Check
                        if not produkt_name or len(produkt_name) < 3 or any(b in produkt_name.lower() for b in blacklist):
                            continue
                        if re.match(r'^[-+]?\d+\s*%?$', produkt_name):
                            continue
                        
                        t = produkt_name.lower()
                        key = "apple" if any(w in t for w in ["apfel", "äpfel", "obst", "banane"]) \
                            else "potato" if "kartoffel" in t \
                            else "fish" if any(w in t for w in ["lachs", "fisch"]) \
                            else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "haribo"]) \
                            else "milkshake" if any(w in t for w in ["spezi", "cola", "wasser", "bier", "saft"]) \
                            else "default"
                        
                        # Formatierung der Ausgabe-Preise mit Komma
                        preis_final = f"{neuer_preis_raw.replace('.', ',')} €"
                        alter_preis_final = f"{alter_preis_raw.replace('.', ',')} €" if alter_preis_raw else ""
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": produkt_name,
                            "preis": preis_final,
                            "alter_preis": alter_preis_final,
                            "rabatt": "", # Keine Prozentzeichen oder Rabatt-Texte mehr
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} Produkte mit Preisvergleich extrahiert ===")
    except Exception as e:
        print(f"Fehler: {e}")

    if not neue_liste:
        neue_liste = [{"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Warte auf PDF-Korrektur", "preis": "0,00 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "KW 42", "bild": "default"}]

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
