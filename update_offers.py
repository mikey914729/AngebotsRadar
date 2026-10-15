import json
import requests


def hole_prospekt_daten():
    plz = "85283"
    url = f"https://discounto.de{plz}&limit=60"

    print(f"Lade Prospekt-Angebote mit Bildern für PLZ {plz}...")

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            raise Exception("API Limit")
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception:
        print("Verwende Wolnzach Prospekt-Katalog-Fallback...")
                # Lokale Bildpfade, die direkt aus deinem eigenen Repository geladen werden
        roh_angebote = [
            {
                "title": "Frische Bio-Bananen (Costa Rica)",
                "merchant": "EDEKA Wolnzach",
                "price": "1.99",
                "old_price": "2.49",
                "valid_until": "Diese Woche",
                "image": "IMG_0190.jpeg"
            },
            {
                "title": "Garnelen pfannenfertig 250g",
                "merchant": "ALDI SÜD Wolnzach",
                "price": "3.49",
                "old_price": "4.29",
                "valid_until": "Diese Woche",
                "image": "garnelen.jpg"
            },
            {
                "title": "Premium Hundefutter Fleisch-Brocken",
                "merchant": "Fressnapf Wolnzach",
                "price": "2.99",
                "old_price": "3.99",
                "valid_until": "Diese Woche",
                "image": "hundefutter.jpg"
            }
        ]
    angebote_liste = []

    for item in roh_angebote:
        merchant_raw = item.get("merchant", "").lower()

        # Saubere Zuordnung für die Filter-Buttons
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
            id_name = "andere"
            label = item.get("merchant", "Anderer Markt")

        # Standardbild setzen, falls die API mal kein Foto liefert
        bild_url = item.get("image") or item.get("image_url") or "https://unsplash.com"

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": f"{item.get('price', '0.00')} €",
            "alter_preis": (
                f"statt {item.get('old_price')} €"
                if item.get("old_price")
                else ""
            ),
            "gueltigkeit": item.get("valid_until", "Diese Woche gültig"),
            "bild": bild_url,
        }
        angebote_liste.append(angebot)

    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print("Prospekt-Daten erfolgreich in daten.json eingetragen!")


if __name__ == "__main__":
    hole_prospekt_daten()
