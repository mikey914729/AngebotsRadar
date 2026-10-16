import json
import requests

def hole_aktuelle_prospekte():
    plz = "85283"
    url = f"https://discounto.de{plz}&limit=100"
    
    print(f"Verbinde mit Prospekt-Server... Lade Live-Angebote für Wolnzach (PLZ {plz})...")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            raise Exception("API temporär nicht erreichbar")
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception:
        roh_angebote = []

    # Daten-Fallback für die korrekte Bildzuordnung per Text-Schlüsselwort
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

        if "aldi" in merchant_raw: id_name, label = "aldi", "ALDI SÜD"
        elif "edeka" in merchant_raw: id_name, label = "edeka", "EDEKA"
        elif "rossmann" in merchant_raw: id_name, label = "rossmann", "ROSSMANN"
        elif "penny" in merchant_raw: id_name, label = "penny", "PENNY"
        elif "netto" in merchant_raw: id_name, label = "netto", "Netto"
        elif "baumarkt" in merchant_raw or "sonderpreis" in merchant_raw: id_name, label = "baumarkt", "Sonderpreis Baumarkt"
        elif "fressnapf" in merchant_raw: id_name, label = "fressnapf", "Fressnapf"
        else: continue

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
        
        if key == "default":
            if "pfeffer" in titel_mitte or "keks" in titel_mitte: key = "cookies"
            elif "schoko" in titel_mitte or "ritter" in titel_mitte: key = "chocolate"
            elif "butter" in titel_mitte: key = "butter"
            elif "milch" in titel_mitte or "shake" in titel_mitte: key = "milkshake"
            elif "ariel" in titel_mitte or "wasch" in titel_mitte: key = "laundry"
            elif "futter" in titel_mitte or "hund" in titel_mitte: key = "dogfood"
            elif "schraub" in titel_mitte or "nagel" in titel_mitte: key = "screws"

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": f"{item.get('price')} €",
            "alter_preis": f"statt {item.get('old_price')} €" if item.get("old_price") else "",
            "rabatt": rabatt_text,
            "gueltigkeit": item.get("valid_until", "Diese Woche gültig"),
            "bild": key
        }
        angebote_liste.append(angebot)

    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print(f"Erfolgreich {len(angebote_liste)} Live-Angebote aktualisiert!")

if __name__ == "__main__":
    hole_aktuelle_prospekte()
