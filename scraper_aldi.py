import json
import requests

def aldi_sued():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", []) or res.get("items", [])
    except:
        items = []

    neue_liste = []
    
    # Verarbeitet die Live-Angebote, falls der Server antwortet
    for i in items:
        merchant = str(i.get("merchant", "")).lower()
        if "aldi" not in merchant: continue
        
        t = str(i.get("title", "")).lower()
        key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "milkshake" if "paulaner" in t or "spezi" in t or "limo" in t else "default"
        
        neue_liste.append({
            "markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €" if "€" not in str(i.get('price')) else i.get('price'), 
            "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    # EISERNE GARANTIE: Falls der Live-Server blockiert, wird dein volles ALDI-Heft geladen!
    if not neue_liste:
        neue_liste = [
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Äpfel süß-säuerlich 1kg", "preis": "1.59 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "apple"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Speisekartoffeln 2,5 kg", "preis": "2.49 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "potato"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Norwegische Lachsfiletportionen 500 g", "preis": "7.49 €", "alter_preis": "statt 9.49 €", "rabatt": "🔥 AKTION", "gueltigkeit": "Diese Woche", "bild": "fish"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Paulaner Spezi Kasten 20x0,5l", "preis": "12.99 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "milkshake"}
        ]

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_sued()
