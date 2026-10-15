import json
import requests

# Koordinaten-Box (Bounding Box) für die Region 85283 (Geisenfeld)
# Format: (Süden, Westen, Norden, Osten)
BBOX = "48.65,11.55,48.72,11.69"

def hole_lokale_maerkte():
    # Overpass API Query für Supermärkte und Marktplätze in der Region
    url = "https://overpass-api.de"
    query = f"""
    [out:json][timeout:25];
    (
      node["shop"="supermarket"]({BBOX});
      node["shop"="bakery"]({BBOX});
      node["amenity"="marketplace"]({BBOX});
    );
    out body;
    """
    
    print("Rufe Daten von der OpenStreetMap API ab...")
    response = requests.post(url, data={"data": query})
    
    if response.status_code != 200:
        print(f"Fehler beim API-Abruf: {response.status_code}")
        return
        
    data = response.json()
    maerkte = []
    
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        markt = {
            "name": tags.get("name", "Unbekannter Laden"),
            "typ": tags.get("shop") or tags.get("amenity"),
            "strasse": tags.get("addr:street", "Keine Straße"),
            "hausnummer": tags.get("addr:housenumber", ""),
            "ort": tags.get("addr:city", "85283 Geisenfeld"),
            "oeffnungszeiten": tags.get("opening_hours", "Nicht angegeben")
        }
        maerkte.append(markt)
        
    # Ergebnisse in JSON-Datei speichern
    with open("daten.json", "w", encoding="utf-8") as f:
        json.dump(maerkte, f, ensure_ascii=False, indent=2)
        
    print(f"Erfolgreich {len(maerkte)} Märkte für 85283 aktualisiert!")

if __name__ == "__main__":
    hole_lokale_maerkte()
