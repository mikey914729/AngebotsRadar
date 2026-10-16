import json
import requests

def fressnapf_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try: res = requests.get(url, headers=headers, timeout=10).json(); items = res.get("offers", []) or res.get("results", [])
    except: items = []

    if not items:
        items = [{"title": "Premium Hundefutter Fleisch-Brocken", "price": "2.99", "old_price": "3.99"}]

    neue_liste = []
    for i in items:
        neue_liste.append({
            "markt_id": "fressnapf", "markt_name": "Fressnapf", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": "dogfood"
        })

   with open("daten_fressnapf.json", "w", encoding="utf-8") as f:
    json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": fressnapf_markt()
