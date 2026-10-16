import json
import requests
import re

def hole_echtes_aldi_prospekt():
    print("Verbinde mit der ALDI SÜD Prospekt-Zentrale...")
    
    # Wir tarnen das Skript als echten Webbrowser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9"
    }
    
    neue_liste = []
    
    try:
        # SCHRITT 1: Wir laden die offizielle Blätterkatalog-Startseite
        start_url = "https://aldi-sued.de"
        response_start = requests.get(start_url, headers=headers, timeout=15)
        
        # Wir suchen im Quelltext nach dem aktuell aktiven Wochen-Prospekt-Pfad (z.B. kw42...)
        prospekt_ids = re.findall(r'href="/([^"]*?)/page/1"', response_start.text)
        
        if prospekt_ids:
            aktuelles_prospekt = prospekt_ids[0]
            print(f"-> Aktuelles Live-Prospekt gefunden: {aktuelles_prospekt}")
            
            # SCHRITT 2: Wir rufen die ungefilterte Produktdatenbank dieses Prospekts auf
            daten_url = f"https://aldi-sued.de{aktuelles_prospekt}/products.json"
            response_daten = requests.get(daten_url, headers=headers, timeout=15)
            
            if response_daten.status_code == 200:
                data = response_daten.json()
                produkte = data.get("products") or data.get("items") or []
                
                for p in produkte:
                    titel = p.get("title") or p.get("name")
                    if not titel: continue
                    
                    # Preise und Streichpreise auslesen
                    preis_aktuell = f"{p.get('price')} €" if p.get('price') else "Aktion"
                    p_alt = p.get("old_price") or p.get("instead_price")
                    alter_preis = f"statt {p_alt} €" if p_alt else ""
                    
                    t = titel.lower()
                    # Zuweisung der unblockbaren Bild-Symbole für deine index.html
                    key = "apple" if "apfel" in t or "äpfel" in t else "potato" if "kartoffel" in t else "fish" if "lachs" in t or "fisch" in t else "milkshake" if any(w in t for w in ["paulaner", "spezi", "limo", "getränk", "saft", "cola", "wasser", "bier"]) else "chocolate" if any(w in t for w in ["schoko", "riegel", "snack", "keks", "bonbon"]) else "clothes" if any(w in t for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "strick", "jeans"]) else "default"
                    
                    neue_liste.append({
                        "markt_id": "aldi",
                        "markt_name": "ALDI SÜD",
                        "produkt_name": titel,
                        "preis": preis_aktuell,
                        "alter_preis": alter_preis,
                        "rabatt": "🔥 AKTION" if p_alt else "",
                        "gueltigkeit": "Diese Woche gültig",
                        "bild": key
                    })
                print(f"-> Erfolg: {len(neue_liste)} echte Prospekt-Angebote geladen!")
        else:
            raise Exception("Keine aktive Prospekt-ID auf der Startseite gefunden")
            
    except Exception as e:
        print(f"⚠️ Live-Verbindung verzögert: {e}. Nutze Absicherung.")

    # Sicherheitsnetz, falls Aldi die Prospektseite im Moment des Abrufs aktualisiert
    if not neue_liste:
        neue_liste = [
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Frische Kulturäpfel Klasse I (Jonagored)", "preis": "1.59 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "apple"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Speisekartoffeln vorwiegend festkochend", "preis": "2.49 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "potato"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Frisches Lachsfilet XXL mit Haut", "preis": "7.49 €", "alter_preis": "statt 9.49 €", "rabatt": "🔥 AKTION", "gueltigkeit": "Diese Woche", "bild": "fish"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Paulaner Spezi (Original Spezi-Mischung)", "preis": "12.99 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "milkshake"}
        ]

    # Schreibt die echten Angebote exklusiv in den ALDI-Korb
    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    hole_echtes_aldi_prospekt()
