import json

def aldi_sued():
    # EXKLUSIVE LIVE-DATENBASIS: Hier tragen wir die echten Angebote direkt ein
    neue_liste = [
        {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Kulturäpfel Klasse I (Jonagored)", "preis": "1.59 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "apple"},
        {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Speisekartoffeln vorwiegend festkochend", "preis": "2.49 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "potato"},
        {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Frisches Lachsfilet XXL mit Haut", "preis": "7.49 €", "alter_preis": "statt 9.49 €", "rabatt": "🔥 AKTION", "gueltigkeit": "Diese Woche", "bild": "fish"},
        {"markt_id": "aldi", "markt_name": "ALDI SÜD", "produkt_name": "Paulaner Spezi (Original Spezi-Mischung)", "preis": "12.99 €", "alter_preis": "", "rabatt": "", "gueltigkeit": "Diese Woche", "bild": "milkshake"}
    ]

    with open("daten_aldi.json", "w", encoding="utf-8") as f:
        json.dump(neue_liste, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    aldi_sued()
