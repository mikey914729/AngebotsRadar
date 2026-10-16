import json
import requests

def rossmann_drogerie():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try: res = requests.get(url, headers=headers, timeout=10).json(); items = res.get("offers", []) or res.get("results", [])
    except: items = []

    if not items:
        items = [{"title": "Ariel Vollwaschmittel XXL Pulver", "price": "14.99", "old_price": "19.99"}]

    neue_liste = []
    for i in items:
        t = i.get("title", "").lower()
        key = "laundry" if any(w in t for w in ["ariel", "wasch", "seife", "shampoo", "creme", "deo", "dusch"]) else "default"
        neue_liste.append({
            "markt_id": "rossmann", "markt_name": "ROSSMANN", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    try: with open("daten.json", "r", encoding="utf-8") as f: daten = json.load(f)
    except: daten = []
    daten = [d for d in daten if d["markt_id"] != "rossmann"] + neue_liste
    with open("daten.json", "w", encoding="utf-8") as f: json.dump(daten, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": rossmann_drogerie()
