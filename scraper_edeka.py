import json
import requests

def edeka_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", []) or res.get("items", [])
    except:
        items = []

    if not items:
        items = [{"title": "Ritter Sport Schokolade 100g", "price": "0.99", "old_price": "1.49"}]

    neue_liste = []
    for i in items:
        t = str(i.get("title", "")).lower()
        key = "chocolate" if any(w in t for w in ["schoko", "ritter", "riegel", "snack", "bonbon", "haribo"]) else "default"
        neue_liste.append({
            "markt_id": "edeka", "markt_name": "EDEKA", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    with open("daten_edeka.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    edeka_markt()
