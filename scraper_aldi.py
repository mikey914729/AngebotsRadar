import json
import logging
import re
import unicodedata
from pathlib import Path
from statistics import median

import pdfplumber


# --------------------------------------------------
# KONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

PDF_DATEI = BASE_DIR / "aldi.pdf"
JSON_DATEI = BASE_DIR / "daten_aldi.json"

MARKT_ID = "aldi"
MARKT_NAME = "ALDI SÜD"
GUELTIGKEIT = "KW 42"

# Räumliche Grenzen in PDF-Punkten.
MAX_ABSTAND_OBEN = 85
MAX_ABSTAND_SEITLICH = 65

# Mindestabstand zwischen getrennten Preisfeldern.
# Die Zuordnung bleibt bewusst konservativ.
MIN_NAME_SCORE = 1.0

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

log = logging.getLogger("aldi")


# --------------------------------------------------
# FILTER UND MUSTER
# --------------------------------------------------

PRICE_RE = re.compile(
    r"(?<![\d.,])"
    r"(\d{1,3}(?:\.\d{3})*[,.]\d{2}|\d+[,.]\d{2})"
    r"\s*€?"
    r"(?![\d.,])"
)

PERCENT_RE = re.compile(
    r"(?<!\d)\d{1,3}\s*%"
)

UNIT_RE = re.compile(
    r"\b("
    r"grundpreis|"
    r"literpreis|"
    r"l-?preis|"
    r"kg-?preis|"
    r"stückpreis|"
    r"stueckpreis|"
    r"je\s*\d|"
    r"pro\s*\d|"
    r"€/kg|€/g|€/l|€/ml|"
    r"eur/kg|eur/l"
    r")\b",
    re.IGNORECASE,
)

QUANTITY_RE = re.compile(
    r"\b\d+(?:[,.]\d+)?\s*"
    r"(?:kg|g|mg|ml|cl|liter|litern|"
    r"l|stk|stück|stueck|meter|m)\b",
    re.IGNORECASE,
)

DATE_RE = re.compile(
    r"\b\d{1,2}[./]\d{1,2}"
    r"(?:[./]\d{2,4})?\b"
)

BLACKLIST = (
    "gutes für alle",
    "gutes fuer alle",
    "mehr auf",
    "dauerhaft",
    "top-deals",
    "best-preis",
    "sparpotenzial",
    "preisvorteil",
    "tiefpreis",
    "wochenangebot",
    "gültig ab",
    "gueltig ab",
    "angebote gültig",
    "angebote gueltig",
    "hintergrund ki-generiert",
    "ki-generiert",
    "im innenteil",
    "aldi informiert",
    "jetzt sparen",
    "nur für kurze zeit",
    "nur fuer kurze zeit",
    "solange der vorrat reicht",
    "aktionspreis",
    "rabatt",
    "prospekt",
    "einfach besser",
    "bewusst einkaufen",
)

GENERIC_RE = re.compile(
    r"^\s*(?:"
    r"statt\b|neu\b|aktion\b|angebot\b|"
    r"dauerhaft\b|ab\s+(?:montag|dienstag|mittwoch|"
    r"donnerstag|freitag|samstag|sonntag)\b|"
    r"-?\d+(?:[,.]\d+)?\s*%?"
    r")\s*$",
    re.IGNORECASE,
)


# --------------------------------------------------
# TEXTBEREINIGUNG
# --------------------------------------------------

def clean_text(text):
    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("\u00ad", "")
    text = text.replace("\u00a0", " ")

    text = re.sub(r"[\u200b-\u200f\ufeff]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip(" \t-–—|:;,")


def is_noise(text):
    text = clean_text(text)

    if len(text) < 3 or len(text) > 90:
        return True

    lower = text.casefold()

    if any(term in lower for term in BLACKLIST):
        return True

    if UNIT_RE.search(lower):
        return True

    if PERCENT_RE.search(text):
        return True

    if QUANTITY_RE.search(text):
        return True

    if DATE_RE.search(text):
        return True

    if GENERIC_RE.fullmatch(text):
        return True

    if not re.search(r"[A-Za-zÄÖÜäöüß]", text):
        return True

    # Viele Zahlen in einem vermeintlichen Produktnamen
    # deuten häufig auf Preis- oder Fußnotentext hin.
    digits = sum(char.isdigit() for char in text)

    if digits / max(len(text), 1) > 0.25:
        return True

    return False


def parse_price(value):
    value = value.strip().replace("€", "").replace(" ", "")

    if not PRICE_RE.fullmatch(value):
        return None

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    else:
        value = value.replace(",", ".")

    try:
        number = float(value)
    except ValueError:
        return None

    if not 0.05 <= number <= 9999.99:
        return None

    return round(number, 2)


def format_price(value):
    if value is None:
        return ""

    return f"{value:.2f}".replace(".", ",") + " €"


# --------------------------------------------------
# WÖRTER UND ZEILEN AUS DEM PDF
# --------------------------------------------------

def get_words(page):
    raw_words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=False,
        extra_attrs=["size"],
    )

    words = []

    for word in raw_words:
        text = clean_text(word.get("text", ""))

        if not text:
            continue

        words.append({
            "text": text,
            "x0": float(word["x0"]),
            "x1": float(word["x1"]),
            "top": float(word["top"]),
            "bottom": float(word["bottom"]),
            "size": float(word.get("size", 0) or 0),
        })

    return sorted(
        words,
        key=lambda word: (word["top"], word["x0"]),
    )


def build_lines(words):
    """
    Gruppiert Wörter anhand ihrer vertikalen Position.
    Die räumlichen Koordinaten bleiben erhalten.
    """
    groups = []

    for word in words:
        center = (word["top"] + word["bottom"]) / 2
        best_group = None
        best_distance = float("inf")

        for group in groups[-10:]:
            group_center = median(
                (item["top"] + item["bottom"]) / 2
                for item in group
            )

            distance = abs(center - group_center)
            tolerance = max(2.5, min(word["size"] * 0.3, 5.0))

            if distance <= tolerance and distance < best_distance:
                best_group = group
                best_distance = distance

        if best_group is None:
            groups.append([word])
        else:
            best_group.append(word)

    lines = []

    for group in groups:
        group.sort(key=lambda word: word["x0"])

        text = clean_text(
            " ".join(word["text"] for word in group)
        )

        if not text:
            continue

        lines.append({
            "text": text,
            "words": group,
            "x0": min(word["x0"] for word in group),
            "x1": max(word["x1"] for word in group),
            "top": min(word["top"] for word in group),
            "bottom": max(word["bottom"] for word in group),
            "size": median(word["size"] for word in group),
        })

    return sorted(lines, key=lambda line: (line["top"], line["x0"]))


# --------------------------------------------------
# PREISFELDER ERKENNEN
# --------------------------------------------------

def extract_prices(lines, words):
    """
    Erkennt Preise in einzelnen Wörtern.

    Preiszeilen mit Grundpreis- oder Rabattkennzeichnung
    werden ausgeschlossen. Kleine Preisfragmente werden
    nicht blind als Angebotspreise interpretiert.
    """
    page_font_sizes = [
        word["size"]
        for word in words
        if word["size"] > 0
    ]

    typical_size = (
        median(page_font_sizes)
        if page_font_sizes
        else 8.0
    )

    prices = []

    for word in words:
        text = word["text"]

        if "%" in text:
            continue

        # Kleingedruckte Preisfragmente überspringen.
        # Diese Schwelle ist eine Heuristik und muss bei
        # Bedarf an das konkrete PDF angepasst werden.
        if word["size"] < typical_size * 0.72:
            continue

        for match in PRICE_RE.finditer(text):
            value = parse_price(match.group(1))

            if value is None:
                continue

            price = {
                "value": value,
                "x0": word["x0"],
                "x1": word["x1"],
                "top": word["top"],
                "bottom": word["bottom"],
                "size": word["size"],
            }

            # Preis im räumlichen Umfeld einer Grundpreiszeile?
            # Hier werden benachbarte Zeilen geprüft, nicht
            # nur das Wort, in dem die Zahl steht.
            is_unit_price = False

            for line in lines:
                vertical_distance = min(
                    abs(line["top"] - price["top"]),
                    abs(line["bottom"] - price["bottom"]),
                )

                if vertical_distance > 12:
                    continue

                horizontal_distance = max(
                    0,
                    line["x0"] - price["x1"],
                    price["x0"] - line["x1"],
                )

                if horizontal_distance > 90:
                    continue

                if UNIT_RE.search(line["text"]):
                    is_unit_price = True
                    break

            if is_unit_price:
                continue

            prices.append(price)

    # Identische Treffer am selben Ort entfernen.
    unique = {}

    for price in prices:
        key = (
            price["value"],
            round(price["x0"] / 3),
            round(price["top"] / 3),
        )

        unique[key] = price

    return list(unique.values())


# --------------------------------------------------
# PRODUKTNAMEN ZUORDNEN
# --------------------------------------------------

def horizontal_distance(a, b):
    if a["x1"] < b["x0"]:
        return b["x0"] - a["x1"]

    if b["x1"] < a["x0"]:
        return a["x0"] - b["x1"]

    return 0.0


def horizontal_overlap(a, b):
    return max(
        0.0,
        min(a["x1"], b["x1"]) - max(a["x0"], b["x0"]),
    )


def score_name(line, price, lines):
    text = line["text"]

    if is_noise(text):
        return -1000

    # Keine Preis- oder Rabattzeile als Produktname.
    if PRICE_RE.fullmatch(text) or PERCENT_RE.search(text):
        return -1000

    vertical_gap = price["top"] - line["bottom"]

    # Produktname oberhalb des Preises bevorzugen.
    if vertical_gap < -2 or vertical_gap > MAX_ABSTAND_OBEN:
        return -1000

    horizontal_gap = horizontal_distance(line, price)

    if horizontal_gap > MAX_ABSTAND_SEITLICH:
        return -1000

    # Begrenzung auf ungefähr dieselbe Produktspalte.
    overlap = horizontal_overlap(line, price)

    score = 10.0
    score -= vertical_gap * 0.09
    score -= horizontal_gap * 0.08
    score += min(line["size"], 30) * 0.35

    if overlap > 0:
        score += min(overlap, 100) * 0.04

    if 2 <= len(text.split()) <= 6:
        score += 1.0

    if len(text.split()) > 8:
        score -= 3.0

    # Slogans mit Satzcharakter sind weniger wahrscheinlich
    # echte Produktüberschriften.
    if text.endswith((".", "!", "?")):
        score -= 2.0

    # Falls zwischen Name und Preis eine weitere Textzeile
    # liegt, wird der Kandidat vorsichtiger bewertet.
    for other in lines:
        if other is line:
            continue

        if not (
            line["bottom"] < other["top"] < price["top"]
        ):
            continue

        gap = other["top"] - line["bottom"]

        if gap > 25:
            continue

        overlap_with_other = horizontal_overlap(line, other)

        if overlap_with_other > 0 and is_noise(other["text"]):
            score -= 1.5

    return score


def find_name(price, lines):
    candidates = []

    for line in lines:
        score = score_name(line, price, lines)

        if score >= MIN_NAME_SCORE:
            candidates.append((score, line))

    if not candidates:
        return None, 0

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best_line = candidates[0]

    # Wenn zwei Kandidaten fast gleich gut passen, ist
    # die Zuordnung mehrdeutig. Nicht blind veröffentlichen.
    if len(candidates) > 1:
        second_score = candidates[1][0]

        if best_score - second_score < 0.75:
            return None, best_score

    name = clean_text(best_line["text"])

    if is_noise(name):
        return None, 0

    return name, best_score


# --------------------------------------------------
# STREICHPREIS
# --------------------------------------------------

def find_old_price(current, prices):
    """
    Konservative Variante:
    Ohne Prüfung der tatsächlichen Durchstreichung wird
    kein alter Preis automatisch behauptet.

    Das verhindert, dass der Preis eines Nachbarprodukts
    als Streichpreis ausgegeben wird.
    """
    return ""


# --------------------------------------------------
# BILDER UND DUPLIKATE
# --------------------------------------------------

def image_key(name):
    lower = name.casefold()

    if "apfel" in lower:
        return "apple"

    if "fisch" in lower:
        return "fish"

    if "schoko" in lower:
        return "chocolate"

    return "default"


def deduplicate(offers):
    unique = []
    seen = set()

    for offer in offers:
        key = (
            re.sub(
                r"\W+",
                " ",
                offer["produkt_name"].casefold(),
            ).strip(),
            offer["preis"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(offer)

    return unique


# --------------------------------------------------
# HAUPTPROGRAMM
# --------------------------------------------------

def aldi_pdf_profi_scanner():
    log.info("ALDI-SÜD-Scanner gestartet")

    if not PDF_DATEI.exists():
        raise FileNotFoundError(
            f"PDF nicht gefunden: {PDF_DATEI}"
        )

    offers = []

    with pdfplumber.open(PDF_DATEI) as pdf:
        log.info("%d PDF-Seiten gefunden", len(pdf.pages))

        for page_number, page in enumerate(pdf.pages, start=1):
            words = get_words(page)

            if not words:
                log.warning(
                    "Seite %d: kein Text gefunden",
                    page_number,
                )
                continue

            lines = build_lines(words)
            prices = extract_prices(lines, words)

            log.info(
                "Seite %d: %d Wörter, %d Preis-Kandidaten",
                page_number,
                len(words),
                len(prices),
            )

            for price in prices:
                name, score = find_name(price, lines)

                if not name:
                    continue

                if is_noise(name):
                    continue

                offers.append({
                    "markt_id": MARKT_ID,
                    "markt_name": MARKT_NAME,
                    "produkt_name": name,
                    "preis": format_price(price["value"]),
                    "alter_preis": find_old_price(price, prices),
                    "rabatt": "",
                    "gueltigkeit": GUELTIGKEIT,
                    "bild": image_key(name),
                })

    offers = deduplicate(offers)

    JSON_DATEI.parent.mkdir(parents=True, exist_ok=True)

    with JSON_DATEI.open("w", encoding="utf-8") as file:
        json.dump(
            offers,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")

    log.info(
        "Fertig: %d Angebote nach %s geschrieben",
        len(offers),
        JSON_DATEI,
    )


if __name__ == "__main__":
    try:
        aldi_pdf_profi_scanner()
    except Exception:
        log.exception("ALDI-Scraper fehlgeschlagen")
        raise
