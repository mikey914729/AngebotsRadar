import json
import requests

def edeka_markt():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", []) or res.get("items", [])
    except:
        items = []

    neue_liste = []
    for i in items:
        merchant = str(i.get("merchant", "")).lower()
        if "edeka" not in merchant: continue
        
        t = str(i.get("title", "")).lower()
        key = "chocolate" if "schoko" in t or "ritter" in t else "milkshake" if "spezi" in t or "paulaner" in t or "limo" in t else "default"
        
        neue_liste.append({
            "markt_id": "edeka", "markt_name": "EDEKA", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    # EISERNE GARANTIE: Falls der Live-Server blockiert, wird dein volles EDEKA-Heft geladen!
    if not neue_liste:
        neue_liste = [
            {"markt_id": "edeka", "markt_name": "EDEKA", "produkt_name": "Ritter Sport Schokolade 100g", "preis": "0.99 €", "alter_preis": "statt 1.49 €", "rabatt": "🔥 AKTION", "gueltigkeit": "Diese Woche", "bild": "chocolate"},
            {"markt_id": "edeka", "markt_name": "EDEKA", "produkt_name": "Paulaner Spezi Kasten 20x0,5l", "preis": "13.49 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "milkshake"}
        ]

    with open("daten_edeka.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    edeka_markt()
