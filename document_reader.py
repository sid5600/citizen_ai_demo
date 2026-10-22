"""Document reader: OCR a scanned form, extract fields, validate them, flag doubtful ones.

Pipeline: image -> OCR (Tesseract, with per-word confidence) -> field extraction
-> format validation -> confidence check -> auto-accept or send to a human officer.
"""
import re
from dataclasses import dataclass

import pytesseract
from PIL import Image, ImageFilter, ImageOps

# Fields below this OCR confidence (0-100) go to an officer for review.
REVIEW_THRESHOLD = 85

# Expected label on the form and the format a valid value must match.
FIELDS = {
    "Name": r"^[A-Za-z][A-Za-z .'-]{2,}$",
    "Date of Birth": r"^\d{2}[-/ ]\w{3}[-/ ]\d{4}$|^\d{2}[-/]\d{2}[-/]\d{4}$",
    "ID Number": r"^[A-Z]{2}\d{7}$",
    "Mobile": r"^\d{10}$",
    "Address": r"^.{8,}$",
}


@dataclass
class FieldResult:
    field: str
    value: str
    confidence: float
    valid_format: bool
    status: str  # "accepted" or "needs review"


def preprocess(image):
    """Grayscale, auto-contrast and mild sharpening help OCR on poor scans."""
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    return gray.filter(ImageFilter.SHARPEN)


def _ocr_lines(image):
    """Group OCR words into text lines, keeping each word's confidence."""
    data = pytesseract.image_to_data(preprocess(image), output_type=pytesseract.Output.DICT)
    lines = {}
    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append((word, float(data["conf"][i])))
    return list(lines.values())


def read_document(image_path):
    """Return one FieldResult per expected field (missing fields need review)."""
    image = Image.open(image_path)
    lines = _ocr_lines(image)
    results = {}

    for words in lines:
        text = " ".join(w for w, _ in words)
        for field, pattern in FIELDS.items():
            if field in results:
                continue
            match = re.match(rf"^\s*{re.escape(field)}\s*[:;.\-]?\s*(.+)$", text, re.IGNORECASE)
            if not match:
                continue
            value = match.group(1).strip()
            # Confidence = average OCR confidence of the words that make up the value.
            n_value_words = len(value.split())
            value_confs = [c for _, c in words[-n_value_words:]]
            confidence = sum(value_confs) / len(value_confs)
            valid = bool(re.match(pattern, value))
            if not valid:
                confidence = min(confidence, 50.0)  # wrong format: do not trust it
            status = "accepted" if confidence >= REVIEW_THRESHOLD and valid else "needs review"
            results[field] = FieldResult(field, value, round(confidence, 1), valid, status)

    for field in FIELDS:
        if field not in results:
            results[field] = FieldResult(field, "", 0.0, False, "needs review")
    return [results[f] for f in FIELDS]


def decide(results):
    """Overall decision for the application."""
    flagged = [r.field for r in results if r.status != "accepted"]
    if not flagged:
        return "AUTO-ACCEPTED: all fields clear, passed to verification against records.", flagged
    return f"SENT TO OFFICER: please check {', '.join(flagged)}.", flagged
