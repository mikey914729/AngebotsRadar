import json
import requests

def aldi_sued():
    # KORREKTUR: Wir suchen live nach aldi UND paulaner für echte Preise!
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
        if "aldi" not in merchant: continue # Nur Aldi-Treffer mitnehmen
        
        t = i.get("title", "").lower()
        key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "milkshake" if "paulaner" in t or "spezi" in t or "limo" in t else "default"
        
        neue_liste.append({
            "markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_sued()
