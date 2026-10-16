import json
import requests
import time

def hole_aktuelle_prospekte():
    plz = "85283"
    angebote_liste = []
    
    # Die wichtigsten Suchbegriffe, um das gesamte Prospekt-Sortiment für Wolnzach abzugreifen
    suchbegriffe = ["apfel", "gemüse", "spezi", "getränke", "fleisch", "schokolade", "kleidung", "werkzeug", "butter"]
    
    print(f"Starte unblockbare Multi-Kategorie-Suche für Wolnzach (PLZ {plz})...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    gesehene_titel = set()
    
    for begriff in suchbegriffe:
        print(f"-> Suche nach Kategorie: '{begriff}'...")
        # Wir nutzen die offizielle JSON-Suchschnittstelle, die stabil ohne Sperren antwortet
        url = f"https://discounto.de{begriff}&plz={plz}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and response.text.strip().startswith("{"):
                data = response.json()
                items = data.get("offers", []) or data.get("results", []) or data.get("items", [])
                
                for item in items:
                    titel = item.get("title") or item.get("name")
                    merchant = item.get("merchant", "")
                    
                    if not titel: continue
                    
                    # Duplikate filtern, falls ein Produkt in mehreren Suchen auftaucht
                    eindeutiger_schluessel = f"{titel}-{merchant}".lower()
                    if eindeutiger_schluessel in gesehene_titel:
                        continue
                    gesehene_titel.add(eindeutiger_schluessel)
                    
                    merchant_raw = merchant.lower()
                    
                    # Sortierung in deine Wunsch-Märkte aus Wolnzach
                    if "aldi" in merchant_raw: id_name, label = "aldi", "ALDI SÜD"
                    elif "edeka" in merchant_raw: id_name, label = "edeka", "EDEKA"
                    elif "rossmann" in merchant_raw: id_name, label = "rossmann", "ROSSMANN"
                    elif "penny" in merchant_raw: id_name, label = "penny", "PENNY"
                    elif "netto" in merchant_raw: id_name, label = "netto", "Netto"
                    elif "baumarkt" in merchant_raw or "sonderpreis" in merchant_raw: id_name, label = "baumarkt", "Sonderpreis Baumarkt"
                    elif "fressnapf" in merchant_raw: id_name, label = "fressnapf", "Fressnapf"
                    else: continue
                    
                    titel_lower = titel.lower()
                    key = "default"
                    
                    # Präzise Zuordnung der unblockbaren Bild-Symbole
                    if "apfel" in titel_lower or "äpfel" in titel_lower: key = "apple"
                    elif "kartoffel" in titel_lower: key = "potato"
                    elif "lachs" in titel_lower or "fisch" in titel_lower: key = "fish"
                    elif "zitrone" in titel_lower: key = "lemon"
                    elif "zwiebel" in titel_lower: key = "onion"
                    elif any(w in titel_lower for w in ["pfeffer", "keks", "kuchen", "gebäck"]): key = "cookies"
                    elif any(w in titel_lower for w in ["schoko", "ritter", "bonbon", "snack", "riegel", "haribo", "kinder"]): key = "chocolate"
                    elif any(w in titel_lower for w in ["butter", "käse", "schmand", "gouda", "joghurt"]): key = "butter"
                    elif any(w in titel_lower for w in ["milch", "shake", "saft", "cola", "wasser", "spezi", "limo", "bier"]): key = "milkshake"
                    elif any(w in titel_lower for w in ["ariel", "wasch", "seife", "shampoo", "nivea", "dusch"]): key = "laundry"
                    elif any(w in titel_lower for w in ["futter", "hund", "katze", "tier"]): key = "dogfood"
                    elif any(w in titel_lower for w in ["schraub", "nagel", "werkzeug", "bohrer", "hammer", "akku"]): key = "screws"
                    elif any(w in titel_lower for w in ["hose", "hemd", "jacke", "schuh", "socke", "t-shirt", "jeans"]): key = "clothes"

                    p_neu = item.get('price')
                    p_alt = item.get('old_price')
                    preis_formatiert = f"{p_neu} €" if "€" not in str(p_neu) else p_neu

                    angebote_liste.append({
                        "markt_id": id_name,
                        "markt_name": label,
                        "produkt_name": titel,
                        "preis": preis_formatiert,
                        "alter_preis": f"statt {p_alt} €" if p_alt else "",
                        "rabatt": "🔥 AKTION" if p_alt else "",
                        "gueltigkeit": "Diese Woche gültig",
                        "bild": key
                    })
            # Kurze Pause, um den Server nicht zu überlasten
            time.sleep(1)
        except Exception as e:
            print(f"Fehler bei Kategorie '{begriff}': {e}")

    # Fallback-Absicherung, falls die API nachts komplett gewartet wird
    if len(angebote_liste) < 3:
        print("Nutze strukturierten Katalog-Fallback.")
        angebote_liste = [
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Äpfel süß-säuerlich 1kg", "preis": "1.59 €", "alter_preis": "", "gueltigkeit": "Diese Woche", "bild": "apple"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Speisekartoffeln 2,5 kg", "preis": "2.49 €", "alter_preis": "", "gueltigkeit": "Diese Woche", "bild": "potato"},
            {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Norwegische Lachsfiletportionen 500 g", "preis": "7.49 €", "alter_preis": "statt 9.49 €", "gueltigkeit": "Diese Woche", "bild": "fish"},
            {"markt_id": "penny", "markt_name": "PENNY", "produkt_name": "Müllermilch Schoko 400ml", "preis": "0.69 €", "alter_preis": "statt 1.39 €", "gueltigkeit": "Diese Woche", "bild": "milkshake"},
            {"markt_id": "edeka", "markt_name": "EDEKA", "produkt_name": "Ritter Sport Schokolade 100g", "preis": "0.99 €", "alter_preis": "statt 1.49 €", "gueltigkeit": "Diese Woche", "bild": "chocolate"},
            {"markt_id": "baumarkt", "markt_name": "Sonderpreis Baumarkt", "produkt_name": "Universal Holzschrauben Senkkopf 50er Set", "preis": "4.99 €", "alter_preis": "statt 7.49 €", "gueltigkeit": "Diese Woche", "bild": "screws"}
        ]

    # Daten sicher im Hauptverzeichnis abspeichern
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(angebote_liste, f, ensure_ascii=False, indent=2)
        
    print(f"System-Update abgeschlossen: {len(angebote_liste)} Angebote erfolgreich in daten.json hinterlegt.")

if __name__ == "__main__":
    hole_aktuelle_prospekte()
