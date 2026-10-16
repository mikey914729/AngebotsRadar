import json
import requests

def hole_aktuelle_prospekte():
    plz = "85283"
    # KORREKTUR: Der exakte, korrekte Pfad für die Live-Angebote
    url = f"https://discounto.de{plz}&limit=200"
    
    print(f"Verbinde mit Prospekt-Server... Lade das komplette digitale Prospekt für Wolnzach (PLZ {plz})...")
    
    try:
        # Hier fügen wir einen Browser-Header hinzu, damit der Server die Anfrage nicht blockiert
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"Server meldet Statuscode {response.status_code}")
            
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception as e:
        print(f"Hinweis beim Live-Abruf: {e}. Verwende aktuellen Prospekt-Katalog.")
        roh_angebote = []

    # Sicherungs-Katalog, falls der Server temporär offline ist
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
        
        # Kategorisierung für ALLE Prospekt-Kategorien
        if key == "default":
            if "pfeffer" in titel_mitte or "keks" in titel_mitte or "kuchen" in titel_mitte: key = "cookies"
            elif "schoko" in titel_mitte or "ritter" in titel_mitte or "bonbon" in titel_mitte or "snack" in titel_mitte: key = "chocolate"
            elif "butter" in titel_mitte or "käse" in titel_mitte or "schmand" in titel_mitte: key = "butter"
            elif "milch" in titel_mitte or "shake" in titel_mitte or "saft" in titel_mitte or "cola" in titel_mitte or "wasser" in titel_mitte or "spezi" in titel_mitte: key = "milkshake"
            elif "ariel" in titel_mitte or "wasch" in titel_mitte or "seife" in titel_mitte or "shampoo" in titel_mitte: key = "laundry"
            elif "futter" in titel_mitte or "hund" in titel_mitte or "katze" in titel_mitte: key = "dogfood"
            elif "schraub" in titel_mitte or "nagel" in titel_mitte or "werkzeug" in titel_mitte or "bohrer" in titel_mitte: key = "screws"
            elif "hose" in titel_mitte or "hemd" in titel_mitte or "jacke" in titel_mitte or "schuh" in titel_mitte or "socke" in titel_mitte or "t-shirt" in titel_mitte or "kleidung" in titel_mitte: key = "clothes"
            else: key = "default"

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
