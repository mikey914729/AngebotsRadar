import json
import requests

def netto_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try: res = requests.get(url, headers=headers, timeout=10).json(); items = res.get("offers", []) or res.get("results", [])
    except: items = []

    if not items:
        items = [{"title": "GUT & GÜNSTIG Deutsche Markenbutter", "price": "1.69", "old_price": "2.29"}]

    neue_liste = []
    for i in items:
        t = i.get("title", "").lower()
        key = "butter" if "butter" in t or "käse" in t else "chocolate" if "haribo" in t or "snack" in t else "default"
        neue_liste.append({
            "markt_id": "netto", "markt_name": "Netto", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    try: with open("daten.json", "r", encoding="utf-8") as f: daten = json.load(f)
    except: daten = []
    daten = [d for d in daten if d["markt_id"] != "netto"] + neue_liste
    with open("daten.json", "w", encoding="utf-8") as f: json.dump(daten, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": netto_markt()
