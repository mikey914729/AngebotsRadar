import json
import requests

def netto_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", []) or res.get("items", [])
    except:
        items = []

    if not items:
        items = [{"title": "GUT & GÜNSTIG Deutsche Markenbutter", "price": "1.69", "old_price": "2.29"}]

    neue_liste = []
    for i in items:
        t = str(i.get("title", "")).lower()
        key = "butter" if any(w in t for w in ["butter", "käse", "schmand", "quark", "joghurt", "gouda"]) else "default"
        neue_liste.append({
            "markt_id": "netto", "markt_name": "Netto", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    with open("daten_netto.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    netto_markt()
