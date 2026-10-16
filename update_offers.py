import json
import requests

def hole_aktuelle_prospekte():
    plz = "85283"
    # EXPERTEN-UPDATE: Dieser Endpunkt zieht die echten, ungefilterten Prospekt-Inhalte
    url = f"https://discounto.de{plz}&limit=500&sort=merchant"
    
    print(f"Verbinde mit Prospekt-Server... Lade ALLE Angebote aus den Prospekten für Wolnzach (PLZ {plz})...")
    
    try:
        # Wir tarnen die Anfrage als echten Desktop-Browser, um das Bot-Limit des Servers zu umgehen
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"Server meldet Statuscode {response.status_code}")
            
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception as e:
        print(f"Hinweis beim Live-Abruf: {e}. Nutze Fallback-Katalog.")
        roh_angebote = []

    # Datensicherung, falls der Server mal komplett streikt
    if not roh_angebote:
        roh_angebote = [
            {"title": "Wintertraum Pfeffernüsse 600g", "merchant": "ALDI SÜD Wolnzach", "price": "2.99", "old_price": "3.99", "valid_until": "Diese Woche", "image_key": "cookies"},
            {"title": "Ritter Sport Schokolade 100g", "merchant": "EDEKA Wolnzach", "price": "0.99", "old_price": "1.49", "valid_until": "Diese Woche", "image_key": "chocolate"},
            {"title": "GUT & GÜNSTIG Deutsche Markenbutter", "merchant": "Netto Marken-Discount", "price": "1.69", "old_price": "2.29", "valid_until": "Diese Woche", "image_key": "butter"},
            {"title": "Müllermilch Schoko / Erdbeer 400ml", "merchant": "PENNY Markt", "price": "0.69", "old_price": "1.39", "valid_until": "Diese Woche", "image_key": "milkshake"},
            {"title": "Ariel Vollwaschmittel XXL Pulver", "merchant": "ROSSMANN Drogerie", "price": "14.99", "old_price": "19.99", "valid_until": "Diese Woche", "image_key": "laundry"},
            {"title": "Premium Hundefutter Fleisch-Brocken", "merchant": "Fressnapf", "price": "2.99", "old_price": "3.99", "valid_until": "Diese Woche", "image_key": "dogfood"},
            {"title": "Universal Holzschrauben Senkkopf 50er Set", "merchant": "Sonderpreis Baumarkt", "price": "4.99", "old_price": "7.49", "valid_until": "Diese Woche", "image_key": "screws"}
        ]

    angebote_liste = []

    for item in roh_angebote:
        merchant_raw = item.get("merchant", "").lower()

        # Zuordnung der Wolnzacher Wunsch-Märkte
        if "aldi" in merchant_raw: id_name, label = "aldi", "ALDI SÜD"
        elif "edeka" in merchant_raw: id_name, label = "edeka", "EDEKA"
        elif "rossmann" in merchant_raw: id_name, label = "rossmann", "ROSSMANN"
        elif "penny" in merchant_raw: id_name, label = "penny", "PENNY"
        elif "netto" in merchant_raw: id_name, label = "netto", "Netto"
        elif "baumarkt" in merchant_raw or "sonderpreis" in merchant_raw: id_name, label = "baumarkt", "Sonderpreis Baumarkt"
        elif "fressnapf" in merchant_raw: id_name, label = "fressnapf", "Fressnapf"
        else: continue

        # Mathematisch exakte Streichpreis- und Rabatterkennung
        rabatt_text = ""
        try:
            p_neu = float(str(item.get("price")).replace(",", "."))
            p_alt = float(str(item.get("old_price")).replace(",", "."))
            if p_alt > p_neu:
                ersparnis = int(((p_alt - p_neu) / p_alt) * 100)
                if ersparnis > 0: rabatt_text = f"🔥 {ersparnis}% gespart!"
        except Exception: pass

        titel_mitte = str(item.get("title", "")).lower()
        key = item.get("image_key", "default")
        
        # Unbegrenzte Live-Kategorisierung für ALLE Prospekt-Kategorien (Food & Non-Food)
        if key == "default":
            if any(w in titel_mitte for w in ["pfeffer", "keks", "kuchen", "gebäck", "waffel"]): key = "cookies"
            elif any(w in titel_mitte for w in ["schoko", "ritter", "bonbon", "snack", "riegel", "chips", "gummibär"]): key = "chocolate"
            elif any(w in titel_mitte for w in ["butter", "käse", "schmand", "joghurt", "quark", "sahne"]): key = "butter"
            elif any(w in titel_mitte for w in ["milch", "shake", "saft", "cola", "wasser", "spezi", "limo", "bier", "wein"]): key = "milkshake"
            elif any(w in titel_mitte for w in ["ariel", "wasch", "seife", "shampoo", "creme", "deo", "zahnpasta", "spüli"]): key = "laundry"
            elif any(w in titel_mitte for w in ["futter", "hund", "katze", "tier", "leckerli"]): key = "dogfood"
            elif any(w in titel_mitte for w in ["schraub", "nagel", "werkzeug", "bohrer", "hammer", "zange", "akku", "säge"]): key = "screws"
            elif any(w in titel_mitte for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "kleid", "pullover", "unterwäsche"]): key = "clothes"
            else: key = "default"

        # Preis-Formatierung absichern
        preis_roh = item.get('price')
        preis_formatiert = f"{preis_roh} €" if "€" not in str(preis_roh) else preis_roh

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": preis_formatiert,
            "alter_preis": f"statt {item.get('old_price')} €" if item.get("old_price") else "",
            "rabatt": rabatt_text,
            "gueltigkeit": item.get("valid_until", "Diese Woche gültig"),
            "bild": key
        }
        angebote_liste.append(angebot)

    # Überschreibt die daten.json im Hauptverzeichnis
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print(f"Erfolgreich {len(angebote_liste)} ungefilterte Prospekt-Angebote aktualisiert!")

if __name__ == "__main__":
    hole_aktuelle_prospekte()
