import json
import requests

def aldi_sued():
    url = "https://discounto.de"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        items = res.get("offers", []) or res.get("results", [])
    except:
        items = []

    # Stamm-Highlights, falls das Live-Internet mal hakt
    if not items:
        items = [
            {"title": "Äpfel süß-säuerlich 1kg", "price": "1.59", "old_price": ""},
            {"title": "Speisekartoffeln 2,5 kg", "price": "2.49", "old_price": ""},
            {"title": "Norwegische Lachsfiletportionen 500 g", "price": "7.49", "old_price": "9.49"}
        ]

    neue_liste = []
    for i in items:
        t = i.get("title", "").lower()
        key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "default"
        
        neue_liste.append({
            "markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": i.get("title"),
            "preis": f"{i.get('price')} €", "alter_preis": f"statt {i.get('old_price')} €" if i.get("old_price") else "",
            "rabatt": "🔥 AKTION" if i.get("old_price") else "", "gueltigkeit": "Diese Woche", "bild": key
        })

    # Wir hängen die Daten an die bestehende Liste an
    try:
        with open("daten.json", "r", encoding="utf-8") as f: daten = json.load(f)
    except: daten = []
    
    # Filtert alte Aldi-Einträge vor dem Speichern raus, damit nichts doppelt ist
    daten = [d for d in daten if d["markt_id"] != "aldi"] + neue_liste
    with open("daten.json", "w", encoding="utf-8") as f: json.dump(daten, f, ensure_ascii=False, indent=2)

if __name__ == "__main__": aldi_sued()
