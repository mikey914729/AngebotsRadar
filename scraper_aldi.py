import json
import re
import pdfplumber

def ist_farbe_rot(non_stroking_color):
    """Prüft, ob die Textfarbe im Prospekt im roten Bereich liegt."""
    if not non_stroking_color:
        return False
        
    # Fall 1: RGB-Farbraum (Werte zwischen 0 und 1)
    if len(non_stroking_color) == 3:
        r, g, b = non_stroking_color
        # Rot muss deutlich dominieren gegenüber Grün und Blau
        return r > 0.6 and g < 0.3 and b < 0.3
        
    # Fall 2: CMYK-Farbraum (Oft bei Druck-PDFs genutzt)
    if len(non_stroking_color) == 4:
        c, m, y, k = non_stroking_color
        # Magenta und Yellow müssen hoch sein, Cyan niedrig (ergibt Rot/Orange)
        return c < 0.2 and m > 0.7 and y > 0.7
        
    return False

def aldi_pdf_profi_scanner():
    print("=== START: REINIGUNGS-SCANNER V8 (FARB- & LAYOUT-ANALYSE) ===")
    neue_liste = []
    
    # Erlaubte Produktwörter zur finalen Absicherung
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
            print(f"-> {len(pdf.pages)} Seiten werden farblich analysiert...")
            
            for page in pdf.pages:
                # Wichtig: Wir fordern die erweiterten Eigenschaften (wie Farbe) an
                words = page.extract_words(extra_attrs=["non_stroking_color"])
                if not words: continue
                
                preis_liste = []
                text_liste = []
                
                for w in words:
                    t_clean = w["text"].strip()
                    farbe = w.get("non_stroking_color")
                    
                    # 1. HÄRTESTER FILTER: Such nach Preisen mit PUNKT
                    if re.search(r'^\d+\.\d{2}$', t_clean):
                        # 2. ZUSATZ-FILTER: Ist die Zahl im Prospekt ROT gedruckt?
                        if ist_farbe_rot(farbe):
                            preis_liste.append(w)
                        else:
                            # Wenn sie nicht rot ist, behandeln wir sie als normalen Text (z.B. alter Preis)
                            text_liste.append(w)
                    else:
                        text_liste.append(w)
                
                # Räumliche Zuordnung der Produkte zum roten Punkt-Preis
                for p in preis_liste:
                    preis_zahl = p["text"]
                    px = (p["x0"] + p["x1"]) / 2
                    py = p["top"]
                    
                    nahe_woerter = []
                    for t in text_liste:
                        tx = (t["x0"] + t["x1"]) / 2
                        ty = t["top"]
                        
                        abstand = ((px - tx)**2 + (py - ty)**2)**0.5
                        # Ein Produktname steht nah dran und meist direkt über/neben dem Preis
                        if abstand < 120 and ty < py + 15: 
                            nahe_woerter.append((abstand, t))
                    
                    if nahe_woerter:
                        nahe_woerter.sort(key=lambda x: x[0])
                        treffer_objekte = [item[1] for item in nahe_woerter[:4]]
                        treffer_objekte.sort(key=lambda x: x["x0"])
                        
                        roher_name = " ".join([o["text"] for o in treffer_objekte]).strip()
                        roher_name_clean = re.sub(r'[^a-zA-Z0-9\säöüÄÖÜß\-\/]', '', roher_name).strip()
                        
                        t_lower = roher_name_clean.lower()
                        
                        # Abgleich mit der Erlaubt-Liste
                        ist_wichtiges_produkt = any(wort in t_lower for wort in erlaubte_kategorien)
                        enthält_muell = any(mü in t_lower for mü in blacklist)
                        
                        if not ist_wichtiges_produkt or enthält_muell or len(roher_name_clean) < 3:
                            continue
                        
                        key = "apple" if "apfel" in t_lower else "fish" if "fisch" in t_lower else "chocolate" if "schoko" in t_lower else "default"
                        
                        neue_liste.append({
                            "markt_id": "aldi",
                            "markt_name": "ALDI SÜD",
                            "produkt_name": roher_name_clean,
                            "preis": f"{preis_zahl.replace('.', ',')} €",
                            "alter_preis": "",
                            "rabatt": "",
                            "gueltigkeit": "KW 42",
                            "bild": key
                        })
                        
        print(f"=== ENDE: {len(neue_liste)} ECHTE rote Aktionsprodukte extrahiert! ===")
    except Exception as e:
        print(f"Fehler bei Farbanalyse: {e}")

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_pdf_profi_scanner()
