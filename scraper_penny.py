import json
import requests

def penny_markt():
    # KORREKTUR: Wir suchen live nach penny UND paulaner für echte Preise!
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", [])
    except:
        items = []

    neue_liste = []
    for i in items:
        merchant = str(i.get("merchant", "")).lower()
        if "penny" not in merchant: continue
        
        t = i.get("title", "").lower()
        key = "milkshake" if any(w in t for w in ["milch", "shake", "spezi", "paulaner", "limo", "cola", "saft"]) else "default"
        
        neue_liste.append({
            "markt_id": "penny", "markt_name": "PENNY", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    with open("daten_penny.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    penny_markt()
