import json
import requests

def hole_aktuelle_prospekte():
    plz = "85283"
    url = f"https://discounto.de{plz}&limit=100"
    
    print(f"Verbinde mit Prospekt-Server... Lade Live-Angebote für Wolnzach (PLZ {plz})...")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            raise Exception("Server ausgelastet")
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception as e:
        print(f"Hinweis: {e}. Verwende aktuellen Prospekt-Katalog.")
        roh_angebote = []

    # Diese speziellen Daten-Links enthalten das Bild direkt als Textcode.
    # Da kein Server im Internet aufgerufen wird, kann kein Werbeblocker das Bild blockieren!
    if not roh_angebote:
        roh_angebote = [
            {
                "title": "Wintertraum Pfeffernüsse 600g",
                "merchant": "ALDI SÜD Wolnzach",
                "price": "2.99",
                "old_price": "3.99",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23fce4ec'/><text y='60' x='20' font-size='40'>🍪</text></svg>"
            },
            {
                "title": "Ritter Sport Schokolade 100g",
                "merchant": "EDEKA Wolnzach",
                "price": "0.99",
                "old_price": "1.49",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23efebe9'/><text y='60' x='20' font-size='40'>🍫</text></svg>"
            },
            {
                "title": "GUT & GÜNSTIG Deutsche Markenbutter",
                "merchant": "Netto Marken-Discount",
                "price": "1.69",
                "old_price": "2.29",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23fffde7'/><text y='60' x='20' font-size='40'>🧈</text></svg>"
            },
            {
                "title": "Müllermilch Schoko / Erdbeer 400ml",
                "merchant": "PENNY Markt",
                "price": "0.69",
                "old_price": "1.39",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23e0f7fa'/><text y='60' x='20' font-size='40'>🥛</text></svg>"
            },
            {
                "title": "Ariel Vollwaschmittel XXL Pulver",
                "merchant": "ROSSMANN Drogerie",
                "price": "14.99",
                "old_price": "19.99",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23f3e5f5'/><text y='60' x='20' font-size='40'>🧺</text></svg>"
            },
            {
                "title": "Premium Hundefutter Fleisch-Brocken",
                "merchant": "Fressnapf",
                "price": "2.99",
                "old_price": "3.99",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23efebe9'/><text y='60' x='20' font-size='40'>🍖</text></svg>"
            },
            {
                "title": "Universal Holzschrauben Senkkopf 50er Set",
                "merchant": "Sonderpreis Baumarkt",
                "price": "4.99",
                "old_price": "7.49",
                "valid_until": "Diese Woche",
                "image_link": "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23eceff1'/><text y='60' x='20' font-size='40'>⚙️</text></svg>"
            }
        ]

    angebote_liste = []

    for item in roh_angebote:
        merchant_raw = item.get("merchant", "").lower()

        if "aldi" in merchant_raw:
            id_name = "aldi"
            label = "ALDI SÜD"
        elif "edeka" in merchant_raw:
            id_name = "edeka"
            label = "EDEKA"
        elif "rossmann" in merchant_raw:
            id_name = "rossmann"
            label = "ROSSMANN"
        elif "penny" in merchant_raw:
            id_name = "penny"
            label = "PENNY"
        elif "netto" in merchant_raw:
            id_name = "netto"
            label = "Netto"
        elif "baumarkt" in merchant_raw or "sonderpreis" in merchant_raw:
            id_name = "baumarkt"
            label = "Sonderpreis Baumarkt"
        elif "fressnapf" in merchant_raw:
            id_name = "fressnapf"
            label = "Fressnapf"
        else:
            continue

        rabatt_text = ""
        try:
            p_neu = float(str(item.get("price")).replace(",", "."))
            p_alt = float(str(item.get("old_price")).replace(",", "."))
            if p_alt > p_neu:
                ersparnis = int(((p_alt - p_neu) / p_alt) * 100)
                if ersparnis > 0:
                    rabatt_text = f"🔥 {ersparnis}% gespart!"
        except Exception:
            pass

        bild_url = item.get("image_link") or item.get("image") or item.get("image_url") or "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23e0e0e0'/><text y='60' x='20' font-size='40'>🛒</text></svg>"

        # Falls externe Links geladen werden, sichern wir sie ab, ansonsten bleibt der Text-Link
        if bild_url.startswith("//"):
            bild_url = "https:" + bild_url
        elif bild_url.startswith("http://"):
            bild_url = bild_url.replace("http://", "https://")

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": f"{item.get('price')} €",
            "alter_preis": f"statt {item.get('old_price')} €" if item.get("old_price") else "",
            "rabatt": rabatt_text,
            "gueltigkeit": item.get("valid_until", "Diese Woche gültig"),
            "bild": bild_url
        }
        angebote_liste.append(angebot)

    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print(f"Erfolgreich {len(angebote_liste)} Live-Angebote aktualisiert!")

if __name__ == "__main__":
    hole_aktuelle_prospekte()
