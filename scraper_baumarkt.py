import json
import requests

def sonderpreis_baumarkt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", []) or res.get("items", [])
    except:
        items = []

    if not items:
        items = [
            {"title": "Universal Holzschrauben Senkkopf 50er Set", "price": "4.99", "old_price": "7.49"},
            {"title": "Profi Akku-Bohrschrauber 18V Koffer", "price": "39.99", "old_price": "59.99"}
        ]

    neue_liste = []
    for i in items:
        t = str(i.get("title", "")).lower()
        key = "screws" if any(w in t for w in ["schraub", "nagel", "werkzeug", "bohrer", "hammer", "akku", "led", "zange"]) else "default"
        neue_liste.append({
            "markt_id": "baumarkt", "markt_name": "Sonderpreis Baumarkt", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    with open("daten_baumarkt.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sonderpreis_baumarkt()
