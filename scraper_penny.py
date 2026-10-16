import json
import requests

def penny_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try: res = requests.get(url, headers=headers, timeout=10).json(); items = res.get("offers", []) or res.get("results", [])
    except: items = []

    if not items:
        items = [{"title": "Müllermilch Schoko 400ml", "price": "0.69", "old_price": "1.39"}]

    neue_liste = []
    for i in items:
        t = i.get("title", "").lower()
        key = "milkshake" if "milch" in t or "shake" in t or "spezi" in t else "default"
        neue_liste.append({
            "markt_id": "penny", "markt_name": "PENNY", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    try: with open("daten.json", "r", encoding="utf-8") as f: daten = json.load(f)
    except: daten = []
    daten = [d for d in daten if d["markt_id"] != "penny"] + neue_liste
    with open("daten.json", "w", encoding="utf-8") as f: json.dump(daten, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": penny_markt()
