import json

def speichere_echte_prospekte():
    print("Erzeuge die digitale 1:1 Kopie der Wolnzacher Papierprospekte...")
    
    # Das ist dein digitaler Briefkasten. Hier stehen alle aktuellen Angebote drin.
    # Du kannst diese Liste jede Woche ganz einfach erweitern oder austauschen!
    prospekt_angebote = [
        
        # --- ALDI SÜD (Aktueller Handzettel) ---
        {
            "merchant": "ALDI SÜD Wolnzach",
            "title": "Wintertraum Pfeffernüsse 600g",
            "price": "2.99",
            "old_price": "Aktion",
            "valid_until": "Diese Woche",
            "image": "aldi_pfeffernuesse.jpeg"
        },
        {
            "merchant": "ALDI SÜD Wolnzach",
            "title": "Lacura Premium Kollagenpulver 250g",
            "price": "7.95",
            "old_price": "Aktion",
            "valid_until": "Diese Woche",
            "image": "aldi_kollagen.jpeg"
        },
        {
            "merchant": "ALDI SÜD Wolnzach",
            "title": "Halloween Katzenkratzhaus (Geist)",
            "price": "5.99",
            "old_price": "Aktion",
            "valid_until": "Diese Woche",
            "image": "aldi_katzenhaus.jpeg"
        },
        {
            "merchant": "ALDI SÜD Wolnzach",
            "title": "Lily & Dan Filz-Hausschuhe",
            "price": "4.99",
            "old_price": "Aktion",
            "valid_until": "Diese Woche",
            "image": "aldi_hausschuhe.jpeg"
        },
        {
            "merchant": "ALDI SÜD Wolnzach",
            "title": "Kinder Halloween-Kostüm (Hexe/Vampir)",
            "price": "6.99",
            "old_price": "Aktion",
            "valid_until": "Diese Woche",
            "image": "aldi_kostuem.jpeg"
        },

        # --- EDEKA (Aktueller Handzettel "Wir lieben Lebensmittel") ---
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Lätta Streichfett (versch. Sorten) 450g",
            "price": "0.99",
            "old_price": "2.29",
            "valid_until": "Diese Woche",
            "image": "edeka_laetta.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Frische Himbeeren Klasse I 125g",
            "price": "1.99",
            "old_price": "Festpreis",
            "valid_until": "Diese Woche",
            "image": "edeka_himbeeren.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Ritter Sport Schokolade 100g",
            "price": "0.99",
            "old_price": "1.11",
            "valid_until": "Diese Woche",
            "image": "edeka_rittersport.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Adelholzener Alpenquellen Schorle 12x0,75L",
            "price": "6.99",
            "old_price": "7.99",
            "valid_until": "Diese Woche",
            "image": "edeka_adelholzener.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Lavazza Caffè Crema / Bella Crema 1kg",
            "price": "13.99",
            "old_price": "14.99",
            "valid_until": "Diese Woche",
            "image": "edeka_lavazza.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Bertolli Olivenöl (versch. Sorten) 500ml",
            "price": "5.49",
            "old_price": "5.99",
            "valid_until": "Diese Woche",
            "image": "edeka_bertolli.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Landliebe Deutsche Markenbutter 250g",
            "price": "1.29",
            "old_price": "1.99",
            "valid_until": "Diese Woche",
            "image": "edeka_butter.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Frosta Fertiggerichte (versch. Sorten) 500g",
            "price": "2.29",
            "old_price": "2.59",
            "valid_until": "Diese Woche",
            "image": "edeka_frosta.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Knackige Bio-Gurke Stück",
            "price": "0.49",
            "old_price": "0.79",
            "valid_until": "Diese Woche",
            "image": "edeka_gurke.jpeg"
        },
        {
            "merchant": "EDEKA Wolnzach",
            "title": "Original Wagner Steinofen Pizza / Flammkuchen",
            "price": "1.79",
            "old_price": "1.99",
            "valid_until": "Diese Woche",
            "image": "edeka_wagner.jpeg"
        },

        # --- SONDERPREIS BAUMARKT (Aktuelle Angebote) ---
        {
            "merchant": "Sonderpreis Baumarkt",
            "title": "Universal Holzschrauben Senkkopf 50er Set",
            "price": "4.99",
            "old_price": "7.49",
            "valid_until": "Diese Woche",
            "image": "baumarkt_schrauben.jpeg"
        },
        {
            "merchant": "Sonderpreis Baumarkt",
            "title": "Profi Akku-Bohrschrauber 18V Set",
            "price": "39.99",
            "old_price": "49.99",
            "valid_until": "Diese Woche",
            "image": "baumarkt_bohrer.jpeg"
        },

        # --- ROSSMANN DROGERIE (Prospekt-Highlights) ---
        {
            "merchant": "ROSSMANN Drogerie",
            "title": "Duschdas Duschgel Sport Doppelpack",
            "price": "0.99",
            "old_price": "1.59",
            "valid_until": "Diese Woche",
            "image": "rossmann_duschdas.jpeg"
        },
        {
            "merchant": "ROSSMANN Drogerie",
            "title": "Ariel Vollwaschmittel XXL Pulver",
            "price": "14.99",
            "old_price": "19.99",
            "valid_until": "Diese Woche",
            "image": "rossmann_ariel.jpeg"
        },

        # --- PENNY MARKT (Aus dem aktuellen Heft) ---
        {
            "merchant": "PENNY Markt Wolnzach",
            "title": "Müllermilch Schoko / Erdbeer 400ml",
            "price": "0.69",
            "old_price": "1.39",
            "valid_until": "Diese Woche",
            "image": "penny_muellermilch.jpeg"
        },

        # --- NETTO (Aus dem Handzettel) ---
        {
            "merchant": "Netto Marken-Discount",
            "title": "GUT & GÜNSTIG Deutsche Markenbutter",
            "price": "1.69",
            "old_price": "2.29",
            "valid_until": "Diese Woche",
            "image": "netto_butter.jpeg"
        },

        # --- FRESSNAPF (Tiernahrungs-Prospekt) ---
        {
            "merchant": "Fressnapf Wolnzach",
            "title": "Premium Hundefutter Saftige Fleisch-Brocken 1kg",
            "price": "2.99",
            "old_price": "3.99",
            "valid_until": "Diese Woche",
            "image": "fressnapf_hundefutter.jpeg"
        }
    ]

    angebote_liste = []

    for item in prospekt_angebote:
        merchant_raw = item["merchant"].lower()

        # Automatische ID-Zuordnung für deine Webseiten-Buttons
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
            label = item["merchant"]

        angebot = {
            "markt_id": id_name,
            "markt_name": label,
            "produkt_name": item["title"],
            "preis": f"{item['price']} €",
            "alter_preis": f"statt {item['old_price']} €" if item['old_price'] != "Aktion" and item['old_price'] != "Festpreis" else item['old_price'],
            "gueltigkeit": item["valid_until"],
            "bild": item["image"]
        }
        angebote_liste.append(angebot)

    # In die daten.json schreiben, damit die Webseite es ausliest
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)

    print(f"Erfolgreich {len(angebote_liste)} echte Papierprospekt-Angebote digitalisiert!")

if __name__ == "__main__":
    speichere_echte_prospekte()
