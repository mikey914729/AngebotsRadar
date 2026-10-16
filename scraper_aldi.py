import json
import re
import pdfplumber

def aldi_pdf_profi_scanner():
    print("=== SCHRITT 1: Starte isolierten PUNKT-PREIS Extraktor ===")
    neue_liste = []
    
    # DATENBANK: Nur Texte, die diese echten Produktwörter enthalten, werden zugelassen!
    erlaubte_kategorien = [
        "kostüm", "kugeln", "deko", "led", "apfel", "äpfel", "lachs", "fisch", 
        "kartoffel", "pommes", "spezi", "limo", "cola", "wasser", "bier", "wein", 
        "schoko", "riegel", "snack", "keks", "bonbon", "haribo", "milka", "hose", 
        "hemd", "jacke", "schuh", "socke", "t-shirt", "jeans", "pullover", "fleisch",
        "wurst", "käse", "milch", "butter", "joghurt", "brot", "brötchen", "ei", "eier"
    ]
    
    blacklist = ["kg-preis", "best-preis", "stückpreis", "grundpreis", "je stück", "je kg", "aktion", "ab mo", "ab do"]

    try:
        with pdfplumber.open("aldi.pdf") as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                if not words: continue
                
                preis_liste = []
                text_liste = []
                
                for w in words:
                    t_clean = w["text"].strip()
                    
                    # DEIN WUNSCH-FILTER: Erkennt NUR Zahlen mit einem PUNKT (z.B. 4.99 oder 12.10)
                    # Reine Komma-Zahlen oder Fließtext-Zahlen werden ignoriert
                    if re.search(r'^\d+\.\d{2}$', t_clean):
                        preis_liste.append(w)
                    else:
                        text_liste.append(w)
                
                # Räumliche Zuordnung der Produkte zum Punkt-Preis
                for p in preis_liste:
                    # Wir behalten den Punkt für das System, konvertieren ihn aber für die Anzeige später in ein Komma
                    preis_zahl = p["text"]
                    px = (p["x0"] + p["x1"]) / 2
                    py = p["top"]
                    
                    nahe_woerter = []
                    for t in text_liste:
                        tx = (t["x0"] + t["x1"]) / 2
                        ty = t["top"]
                        
                        abstand = ((px - tx)**2 + (py - ty)**2)**0.5
                        if abstand < 120 and ty < py + 15: 
                            nahe_woerter.append((abstand, t))
                    
                    if nahe_woerter:
                        nahe_woerter.sort(key=lambda x: x[0])
                        treffer_objekte = [item[1] for item in nahe_woerter[:4]]
                        treffer_objekte.sort(key=lambda x: x["x0"])
                        
                        roher_name = " ".join([o["text"] for o in treffer_objekte]).strip()
                        roher_name_clean = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', roher_name).strip()
                        
                        t_lower = roher_name_clean.lower()
                        
                        # Abgleich mit unserer erlaubten Produkt-Wort-Datei
                        ist_wichtiges_produkt = any(wort in t_lower for wort in erlaubte_kategorien)
                        enthält_muell = any(mü in t_lower for mü in blacklist)
                        
                        if not ist_wichtiges_produkt or enthält_muell or len(roher_name_clean) < 3:
                            continue
                        
                        # Smiley-Zuweisung
                        key = "apple" if "apfel" in t_lower else "fish" if "fisch" in t_lower else "chocolate" if "schoko" in t_lower else "default"
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": roher_name_clean,
                            "preis": f"{preis_zahl.replace('.', ',')} €", # Für die Anzeige schön mit Komma
                            "alter_preis": "",
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} ECHTE Produkte mit Punkt-Preisen gefiltert! ===")
    except Exception as e:
        print(f"Fehler: {e}")

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
