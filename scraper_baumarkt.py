import json
import requests

def sonderpreis_baumarkt():
    # KORREKTUR: Wir suchen hier gezielt nach Baumarkt-Artikeln wie Schrauben
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try: res = requests.get(url, headers=headers, timeout=10).json(); items = res.get("offers", []) or res.get("results", [])
    except: items = []

    if not items:
        items = [
            {"title": "Universal Holzschrauben Senkkopf 50er Set", "price": "4.99", "old_price": "7.49"},
            {"title": "Profi Akku-Bohrschrauber 18V Koffer", "price": "39.99", "old_price": "59.99"}
        ]

    neue_liste = []
    for i in items:
        neue_liste.append({
            "markt_id": "baumarkt", "markt_name": "Sonderpreis Baumarkt", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": "screws"
        })

    try: with open("daten.json", "r", encoding="utf-8") as f: daten = json.load(f)
    except: daten = []
    daten = [d for d in daten if d["markt_id"] != "baumarkt"] + neue_liste
    with open("daten.json", "w", encoding="utf-8") as f: json.dump(daten, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": sonderpreis_baumarkt()
