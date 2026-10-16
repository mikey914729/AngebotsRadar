import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== START: REINIGUNGS-SCANNER V11 (ALLE PRODUKTE ZURÜCK) ===")
    neue_liste = []
    
    # Diese Begriffe werden mitten aus dem Namen herausgelöscht, damit der Name sauber wird
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
                
                preis_liste = []
                text_liste = []
                
                for w in words:
                    t_clean = w["text"].strip()
                    # Such nach Preisen mit PUNKT
                    if re.search(r'^\d+\.\d{2}$', t_clean):
                        preis_liste.append(w)
                    else:
                        text_liste.append(w)
                
                for p in preis_liste:
                    preis_zahl = p["text"]
                    px = (p["x0"] + p["x1"]) / 2
                    py = p["top"]
                    
                    nahe_woerter = []
                    for t in text_liste:
                        tx = (t["x0"] + t["x1"]) / 2
                        ty = t["top"]
                        
                        abstand = ((px - tx)**2 + (py - ty)**2)**0.5
                        # Suchradius, um den Namen über/neben dem Preis zu greifen
                        if abstand < 130 and ty < py + 15: 
                            nahe_woerter.append((abstand, t))
                    
                    if nahe_woerter:
                        nahe_woerter.sort(key=lambda x: x)
                        # Wir nehmen die nahesten Textbausteine
                        treffer_objekte = [item for item in nahe_woerter[:5]]
                        treffer_objekte.sort(key=lambda x: x["x0"])
                        
                        roher_name = " ".join([o["text"] for o in treffer_objekte]).strip()
                        
                        # BEREINIGUNG: Wir löschen den Müll direkt aus dem Text-String
                        name_clean = roher_name
                        for mw in muell_woerter:
                            # Ersetzt das Müllwort unabhängig von Groß-/Kleinschreibung
                            name_clean = re.sub(re.escape(mw), "", name_clean, flags=re.IGNORECASE)
                        
                        # Reine Zahlenkolonnen (wie 2399, 713) herauslöschen
                        name_clean = re.sub(r'\b\d{3,4}\b', "", name_clean)
                        
                        # Doppelte Leerzeichen und Sonderzeichen entfernen
                        name_clean = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', name_clean)
                        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
                        
                        # Wenn nach der Reinigung noch ein echter Text übrig bleibt, nehmen wir ihn!
                        if len(name_clean) < 3:
                            continue
                        
                        t_lower = name_clean.lower()
                        key = "apple" if "apfel" in t_lower else "fish" if "fisch" in t_lower else "chocolate" if "schoko" in t_lower else "default"
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": name_clean,
                            "preis": f"{preis_zahl.replace('.', ',')} €",
                            "alter_preis": "",
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} Produkte erfolgreich geladen! ===")
    except Exception as e:
        print(f"Fehler: {e}")

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
