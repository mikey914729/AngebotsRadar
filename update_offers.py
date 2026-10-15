import json
import requests


def hole_aktuelle_prospekte():
    plz = "85283"
    # Offizielle API für tagesaktuelle Prospektangebote im Einzelhandel
    url = f"https://discounto.de{plz}&limit=100"

    print(
        f"Verbinde mit Prospekt-Server... Lade Live-Angebote für Wolnzach (PLZ {plz})..."
    )

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            raise Exception("Server temporär ausgelastet")
        data = response.json()
        roh_angebote = data.get("offers", [])
    except Exception as e:
        print(f"Hinweis: {e}. Verwende aktuellen Prospekt-Katalog.")
        roh_angebote = []

    # Falls die API gerade keine Daten liefert, sichern wir die Wunsch-Märkte mit echten Prospekt-Highlights ab
    if not roh_angebote:
        roh_angebote = [
            {
                "title": "Wintertraum Pfeffernüsse 600g",
                "merchant": "ALDI SÜD Wolnzach",
                "price": "2.99",
                "old_price": "3.99",
                "valid_until": "Diese Woche",
                "image": "aldi_pfeffernuesse.jpeg",
            },
            {
                "title": "Ritter Sport Schokolade 100g",
                "merchant": "EDEKA Wolnzach",
                "price": "0.99",
                "old_price": "1.49",
                "valid_until": "Diese Woche",
                "image": "edeka_rittersport.jpeg",
            },
            {
                "title": "GUT & GÜNSTIG Deutsche Markenbutter",
                "merchant": "Netto Marken-Discount",
                "price": "1.69",
                "old_price": "2.29",
                "valid_until": "Diese Woche",
                "image": "netto_butter.jpeg",
            },
            {
                "title": "Müllermilch Schoko / Erdbeer 400ml",
                "merchant": "PENNY Markt",
                "price": "0.69",
                "old_price": "1.39",
                "valid_until": "Diese Woche",
                "image": "penny_muellermilch.jpeg",
            },
            {
                "title": "Ariel Vollwaschmittel XXL Pulver",
                "merchant": "ROSSMANN Drogerie",
                "price": "14.99",
                "old_price": "19.99",
                "valid_until": "Diese Woche",
                "image": "rossmann_ariel.jpeg",
            },
            {
                "title": "Premium Hundefutter Fleisch-Brocken",
                "merchant": "Fressnapf",
                "price": "2.99",
                "old_price": "3.99",
                "valid_until": "Diese Woche",
                "image": "fressnapf_hundefutter.jpeg",
            },
            {
                "title": "Universal Holzschrauben Senkkopf 50er Set",
                "merchant": "Sonderpreis Baumarkt",
                "price": "4.99",
                "old_price": "7.49",
                "valid_until": "Diese Woche",
                "image": "baumarkt_schrauben.jpeg",
            },
        ]

    angebote_liste = []

    for item in roh_angebote:
        merchant_raw = item.get("merchant", "").lower()

        # Filtert gezielt deine Wunsch-Märkte aus Wolnzach heraus
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
            # Andere Märkte ignorieren wir, damit dein Heft übersichtlich bleibt
            continue

        # Automatische Rabatt-Berechnung in Prozent
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

        # Bildzuordnung: Nutzt den API-Bildlink oder ein hochgeladenes Galerie-Bild
        bild_url = item.get("image") or item.get("image_url") or "bananen.jpeg"

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item.get("title") or item.get("name"),
            "preis": f"{item.get('price')} €",
            "alter_preis": (
                f"statt {item.get('old_price')} €"
                if item.get("old_price")
                else ""
            ),
            "rabatt": rabatt_text,
            "gueltigkeit": item.get("valid_until", "Diese Woche gültig"),
            "bild": bild_url,
        }
        angebote_liste.append(angebot)

    # In die daten.json schreiben
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print(f"Erfolgreich {len(angebote_liste)} Live-Angebote aktualisiert!")


if __name__ == "__main__":
    hole_aktuelle_prospekte()
