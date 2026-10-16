
import json
import re
import logging
from pathlib import Path
from statistics import median

import pdfplumber


PDF_DATEI = Path("aldi.pdf")
JSON_DATEI = Path("daten_aldi.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Produktunabhängige Werbe- und Systemtexte
BLACKLIST = [
    "gutes für alle",
    "mehr auf",
    "dauerhaft",
    "kg-preis",
    "l-preis",
    "grundpreis",
    "stückpreis",
    "best-preis",
    "sparpotenzial",
    "top-deals",
    "gültig ab",
    "wochenangebot",
    "prospekt",
    "rabatt",
    "aktion",
    "billiger",
    "sparen",
    "tiefpreis",
    "preisvorteil",
]

NOISE_RE = re.compile(
    r"(?:"
    r"\b\d{1,3}\s*%\b"
    r"|\b\d+(?:[,.]\d+)?\s*[- ]?"
    r"(?:kg|mg|ml|cl|liter|gramm)\b"
    r"|\b\d+(?:[,.]\d+)?\s*l[- ]flasche\b"
    r"|€/ ?(?:kg|g|l|ml)\b"
    r"|/\s*(?:kg|g|l|ml)\b"
    r"|(?:ab|von)\s+(?:mo|di|mi|do|fr|sa|so)\b"
    r")",
    re.IGNORECASE,
)

# Absichtlich nur explizite Dezimalpreise:
# 1,99 / 1.99 / 12,99
PRICE_RE = re.compile(
    r"(?<![\w])(\d{1,3}[,.]\d{2})\s*€?(?!\d)"
)

DATE_RE = re.compile(
    r"\b\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?\b"
)


def clean_text(text):
    text = text.replace("\u00ad", "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[\u200b-\u200f\ufeff]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \t-–—|:;,")


def is_noise(text):
    text = clean_text(text)

    if len(text) < 3 or len(text) > 100:
        return True

    lower = text.lower()

    if any(term in lower for term in BLACKLIST):
        return True

    if DATE_RE.search(text):
        return True

    if NOISE_RE.search(text):
        return True

    if not re.search(r"[A-Za-zÄÖÜäöüß]", text):
        return True

    if re.fullmatch(r"[-+]?\d+(?:[,.]\d+)?\s*%?", text):
        return True

    # Reine Preisfragmente sind niemals Produktnamen.
    if re.fullmatch(r"\d{1,3}[,.]\d{2}\s*€?", text):
        return True

    return False


def get_words(page):
    """Wörter einschließlich ihrer PDF-Positionen extrahieren."""
    raw = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=False,
        extra_attrs=["size"],
    )

    words = []

    for w in raw:
        text = clean_text(w.get("text", ""))

        if not text:
            continue

        words.append({
            "text": text,
            "x0": float(w["x0"]),
            "x1": float(w["x1"]),
            "top": float(w["top"]),
            "bottom": float(w["bottom"]),
            "size": float(w.get("size", 0) or 0),
        })

    return sorted(words, key=lambda w: (w["top"], w["x0"]))


def build_lines(words):
    """
    Bildet Zeilen nur aus Wörtern mit ähnlicher vertikaler Lage.
    Die horizontale Position bleibt erhalten.
    """
    lines = []

    for word in words:
        target = None

        for line in lines:
            center = median(
                (item["top"] + item["bottom"]) / 2
                for item in line
            )
            word_center = (word["top"] + word["bottom"]) / 2

            if abs(center - word_center) <= max(
                3.0, word["size"] * 0.4
            ):
                target = line
                break

        if target is None:
            lines.append([word])
        else:
            target.append(word)

    result = []

    for line in lines:
        line.sort(key=lambda w: w["x0"])

        result.append({
            "words": line,
            "text": clean_text(
                " ".join(w["text"] for w in line)
            ),
            "x0": min(w["x0"] for w in line),
            "x1": max(w["x1"] for w in line),
            "top": min(w["top"] for w in line),
            "bottom": max(w["bottom"] for w in line),
            "size": median(
                w["size"] for w in line
            ),
        })

    return sorted(result, key=lambda line: line["top"])


def extract_prices(words, page_number):
    """
    Ermittelt explizite Dezimalpreise.
    Reine Prozentzahlen werden nicht als Preis interpretiert.
    """
    prices = []

    for word in words:
        text = word["text"]

        if "%" in text:
            continue

        for match in PRICE_RE.finditer(text):
            raw_price = match.group(1)

            try:
                value = float(raw_price.replace(",", "."))
            except ValueError:
                continue

            if not 0.05 <= value <= 9999.99:
                continue

            prices.append({
                "text": raw_price,
                "value": round(value, 2),
                "x0": word["x0"],
                "x1": word["x1"],
                "top": word["top"],
                "bottom": word["bottom"],
                "size": word["size"],
                "page": page_number,
            })

    # Doppelte Treffer am gleichen Ort entfernen.
    unique = {}

    for price in prices:
        key = (
            price["value"],
            round(price["x0"] / 4),
            round(price["top"] / 4),
        )
        unique[key] = price

    return list(unique.values())


def score_name(line, price):
    """Bewertet eine mögliche Produktnamen-Zuordnung."""
    text = line["text"]

    if is_noise(text):
        return -1000

    # Produktname sollte im Regelfall oberhalb des Preises stehen.
    vertical_gap = price["top"] - line["bottom"]

    if vertical_gap < -2 or vertical_gap > 100:
        return -1000

    if not 3 <= len(text) <= 100:
        return -1000

    # Nur Kandidaten aus derselben ungefähren Produktspalte.
    if line["x0"] > price["x1"] + 160:
        return -1000

    if line["x1"] < price["x0"] - 160:
        return -1000

    horizontal_gap = max(
        0,
        line["x0"] - price["x1"],
        price["x0"] - line["x1"],
    )

    score = 5.0
    score -= vertical_gap * 0.04
    score -= horizontal_gap * 0.02
    score += min(line["size"], 18) * 0.12

    if len(text.split()) >= 2:
        score += 1.0

    if len(text.split()) > 9:
        score -= 2.0

    if text.isupper() and len(text.split()) >= 4:
        score -= 1.5

    return score


def find_name(price, lines):
    candidates = []

    for line in lines:
        score = score_name(line, price)

        if score > 0:
            candidates.append((score, line))

    if not candidates:
        return None, -1000

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    score, line = candidates[0]
    name = clean_text(line["text"])

    # Keine automatischen Zeilensprünge über mehrere Produktkarten.
    if is_noise(name):
        return None, -1000

    return name, score


def find_old_price(current, prices):
    """
    Liefert nur einen möglichen Vergleichspreis.
    Ohne sichtbare Durchstreichung ist die Zuordnung nicht beweisbar.
    """
    candidates = []

    for other in prices:
        if other is current:
            continue

        if other["value"] <= current["value"]:
            continue

        dy = abs(other["top"] - current["top"])
        dx = abs(other["x0"] - current["x0"])

        if dy <= 12 and dx <= 90:
            candidates.append((dy + dx * 0.2, other["value"]))

    if not candidates:
        return ""

    candidates.sort(key=lambda item: item[0])
    return f'{candidates[0][1]:.2f}'.replace(".", ",") + " €"


def image_key(name):
    lower = name.lower()

    if "apfel" in lower:
        return "apple"

    if "fisch" in lower:
        return "fish"

    if "schoko" in lower:
        return "chocolate"

    return "default"


def aldi_pdf_profi_scanner():
    print("=== START: ALDI LAYOUT-SCANNER ===")

    neue_liste = []

    if not PDF_DATEI.exists():
        raise FileNotFoundError(
            f"PDF nicht gefunden: {PDF_DATEI}"
        )

    with pdfplumber.open(PDF_DATEI) as pdf:
        print(f"-> {len(pdf.pages)} Seiten werden analysiert")

        for page_number, page in enumerate(pdf.pages, start=1):
            words = get_words(page)

            if not words:
                logging.warning(
                    "Seite %s: kein extrahierbarer Text",
                    page_number,
                )
                continue

            lines = build_lines(words)
            prices = extract_prices(words, page_number)

            logging.info(
                "Seite %s: %s Wörter, %s Preise",
                page_number,
                len(words),
                len(prices),
            )

            for price in prices:
                name, score = find_name(price, lines)

                # Lieber ein Angebot überspringen als einen
                # offensichtlich schwachen Treffer veröffentlichen.
                if not name or score < 3.5:
                    continue

                if is_noise(name):
                    continue

                neue_liste.append({
                    "markt_id": "aldi",
                    "markt_name": "ALDI SÜD",
                    "produkt_name": name,
                    "preis": (
                        f'{price["value"]:.2f}'.replace(".", ",")
                        + " €"
                    ),
                    "alter_preis": find_old_price(price, prices),
                    "rabatt": "",
                    "gueltigkeit": "KW 42",
                    "bild": image_key(name),
                })

    # Duplikate vermeiden, verschiedene Preise aber nicht blind
    # zusammenführen.
    unique = []
    seen = set()

    for offer in neue_liste:
        key = (
            offer["produkt_name"].casefold(),
            offer["preis"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(offer)

    with JSON_DATEI.open("w", encoding="utf-8") as file:
        json.dump(
            unique,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"=== ENDE: {len(unique)} Kandidaten gespeichert ===")


if __name__ == "__main__":
    try:
        aldi_pdf_profi_scanner()
    except Exception as exc:
        logging.exception("ALDI-Scraper fehlgeschlagen: %s", exc)
        raise
