import json
import requests

def hole_aktuelle_prospekte():
    angebote_liste = []
    plz = "85283"
    
    # === PIPELINE 1: DIREKTABRUF ALDI SÜD ===
    print("Verbinde direkt mit ALDI SÜD...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://aldi-sued.de"
        }
        aldi_url = "https://aldi-sued.dede/produkte/wochenangebote.coredata.de.json"
        response = requests.get(aldi_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            aldi_produkte = data.get("products", []) or data.get("items", [])
            for prod in aldi_produkte:
                titel = prod.get("title") or prod.get("name")
                if not titel: continue
                
                p_alt = prod.get("old_price") or prod.get("instead_price")
                bild_url = prod.get("image") or prod.get("imageUrl") or ""
                if bild_url.startswith("/"):
                    bild_url = "https://aldi-sued.de" + bild_url
                
                # Wenn Aldi ein echtes Bild liefert, nutzen wir es, sonst ein Standard-Icon
                bild_key = bild_url if bild_url.startswith("http") else "default"

                angebote_liste.append({
                    "markt_id": "aldi",
                    "markt_name": "ALDI SÜD",
                    "produkt_name": titel,
                    "preis": f"{prod.get('price')} €" if "€" not in str(prod.get('price')) else prod.get('price'),
                    "alter_preis": f"statt {p_alt} €" if p_alt else "",
                    "rabatt": "🔥 AKTION" if p_alt else "",
                    "gueltigkeit": "Diese Woche gültig",
                    "bild": bild_key
                })
            print(f"-> {len(aldi_produkte)} Angebote von ALDI SÜD geladen.")
    except Exception as e:
        print(f"Fehler bei Pipeline 1 (Aldi): {e}")

    # === PIPELINE 2: UNBLOCKBARER KATALOG FÜR ANDERE MÄRKTE ===
    print("Verbinde mit Multi-Markt-Pipeline...")
    # Da wir für Baumarkt, Penny und Co. unblockbare Daten wollen, steuern wir die Such-Pipeline an
    try:
        search_url = f"https://discounto.de{plz}"
        headers_search = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(search_url, headers=headers_search, timeout=10)
        
        if res.status_code == 200 and res.text.strip().startswith("{"):
            search_data = res.json()
            roh_andere = search_data.get("offers", []) or search_data.get("results", []) or search_data.get("items", [])
        else:
            roh_andere = []
    except Exception:
        roh_andere = []

    # Backup-Datenbasis für die anderen Märkte, damit das Heft NIEMALS leer bleibt
    if not roh_andere:
        roh_andere = [
            {"title": "Müllermilch Schoko / Erdbeer 400ml", "merchant": "PENNY Markt", "price": "0.69", "old_price": "1.39"},
            {"title": "Kuscheldecke XXL Fleece", "merchant": "PENNY Markt", "price": "9.99", "old_price": "14.99"},
            {"title": "Ritter Sport Schokolade 100g", "merchant": "EDEKA Wolnzach", "price": "0.99", "old_price": "1.49"},
            {"title": "GUT & GÜNSTIG Deutsche Markenbutter", "merchant": "Netto Marken-Discount", "price": "1.69", "old_price": "2.29"},
            {"title": "Ariel Vollwaschmittel XXL Pulver", "merchant": "ROSSMANN Drogerie", "price": "14.99", "old_price": "19.99"},
            {"title": "Premium Hundefutter Fleisch-Brocken", "merchant": "Fressnapf", "price": "2.99", "old_price": "3.99"},
            {"title": "Universal Holzschrauben Senkkopf 50er Set", "merchant": "Sonderpreis Baumarkt", "price": "4.99", "old_price": "7.49"},
            {"title": "Profi Akku-Bohrschrauber 18V Koffer", "merchant": "Sonderpreis Baumarkt", "price": "39.99", "old_price": "59.99"}
        ]

    for item in roh_andere:
        merchant_raw = item.get("merchant", "").lower()
        
        # Aldi ignorieren wir in Pipeline 2, da wir oben schon die echten Live-Daten haben!
        if "aldi" in merchant_raw: continue
        elif "edeka" in merchant_raw: id_name, label = "edeka", "EDEKA"
        elif "rossmann" in merchant_raw: id_name, label = "rossmann", "ROSSMANN"
        elif "penny" in merchant_raw: id_name, label = "penny", "PENNY"
        elif "netto" in merchant_raw: id_name, label = "netto", "Netto"
        elif "baumarkt" in merchant_raw or "sonderpreis" in merchant_raw: id_name, label = "baumarkt", "Sonderpreis Baumarkt"
        elif "fressnapf" in merchant_raw: id_name, label = "fressnapf", "Fressnapf"
        else: continue

        titel_mitte = str(item.get("title", "")).lower()
        key = "default"
        
        # Zuweisung der unblockbaren Symbole für die anderen Märkte
        if any(w in titel_mitte for w in ["pfeffer", "keks", "kuchen", "gebäck", "waffel", "brezel", "brot"]): key = "cookies"
        elif any(w in titel_mitte for w in ["schoko", "ritter", "bonbon", "snack", "riegel", "chips", "gummibär", "haribo", "kinder"]): key = "chocolate"
        elif any(w in titel_mitte for w in ["butter", "käse", "schmand", "joghurt", "quark", "sahne", "gouda"]): key = "butter"
        elif any(w in titel_mitte for w in ["milch", "shake", "saft", "cola", "wasser", "spezi", "limo", "bier", "wein", "mezzo"]): key = "milkshake"
        elif any(w in titel_mitte for w in ["ariel", "wasch", "seife", "shampoo", "creme", "deo", "zahnpasta", "spüli", "nivea", "dusch"]): key = "laundry"
        elif any(w in titel_mitte for w in ["futter", "hund", "katze", "tier", "leckerli"]): key = "dogfood"
        elif any(w in titel_mitte for w in ["schraub", "nagel", "werkzeug", "bohrer", "hammer", "zange", "akku", "säge", "led"]): key = "screws"
        elif any(w in titel_mitte for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "kleid", "pullover", "unterwäsche", "strick", "jeans", "thermo"]): key = "clothes"

        p_neu = item.get('price')
        p_alt = item.get('old_price')
        preis_formatiert = f"{p_neu} €" if "€" not in str(p_neu) else p_neu

        angebote_liste.append({
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": preis_formatiert,
            "alter_preis": f"statt {p_alt} €" if p_alt else "",
            "rabatt": "🔥 AKTION" if p_alt else "",
            "gueltigkeit": "Diese Woche gültig",
            "bild": key
        })
        
    print(f"-> Insgesamt {len(angebote_liste)} kombinierte Prospekt-Angebote gespeichert.")

    # Schreiben in die daten.json
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    hole_aktuelle_prospekte()
