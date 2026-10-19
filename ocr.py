"""
ocr.py - OCR prescription scanner
Uses pytesseract + Pillow to extract medicine names and dosage info
from uploaded prescription images.
"""

import re
from typing import Optional
from PIL import Image, ImageFilter, ImageEnhance
import io

# Graceful import so app loads even if tesseract isn't installed
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# Common medicine/prescription keywords to help highlight relevant lines
MEDICINE_KEYWORDS = [
    "tablet", "tab", "capsule", "cap", "syrup", "mg", "ml", "mcg",
    "injection", "inj", "cream", "ointment", "drops", "patch",
    "twice", "once", "daily", "morning", "evening", "night",
    "before", "after", "meal", "food", "hours", "days", "weeks",
    "rx", "take", "apply", "use", "dose", "dosage",
]

COMMON_MEDICINES = [
    "paracetamol", "aspirin", "ibuprofen", "amoxicillin", "metformin",
    "atorvastatin", "lisinopril", "omeprazole", "azithromycin",
    "cetirizine", "pantoprazole", "amlodipine", "metoprolol",
    "losartan", "gabapentin", "sertraline", "fluoxetine", "ramipril",
    "clopidogrel", "insulin", "prednisone", "doxycycline", "ciprofloxacin",
    "levothyroxine", "warfarin", "furosemide", "hydrochlorothiazide",
    "diclofenac", "ranitidine", "alprazolam", "clonazepam",
]


def _preprocess_image(image: Image.Image) -> Image.Image:
    """
    Improve OCR accuracy by preprocessing the image:
    - Convert to greyscale
    - Increase contrast
    - Apply mild sharpening
    - Resize if small
    """
    img = image.convert("L")  # Grayscale

    # Resize if too small
    w, h = img.size
    if w < 800:
        scale = 800 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    return img


def extract_text_from_image(image_bytes: bytes) -> tuple[bool, str, str]:
    """
    Run OCR on image bytes.
    Returns (success: bool, raw_text: str, error_message: str).
    """
    if not TESSERACT_AVAILABLE:
        return (
            False,
            "",
            "pytesseract is not installed. Please install it and ensure "
            "Tesseract-OCR is available on your system.",
        )

    try:
        image = Image.open(io.BytesIO(image_bytes))
        processed = _preprocess_image(image)

        # Try multiple PSM modes and pick the best result
        configs = [
            "--psm 6",   # Assume a single uniform block of text
            "--psm 4",   # Assume a single column
            "--psm 3",   # Fully automatic (default)
        ]
        best_text = ""
        for cfg in configs:
            try:
                text = pytesseract.image_to_string(processed, config=cfg)
                if len(text.strip()) > len(best_text.strip()):
                    best_text = text
            except Exception:
                continue

        if not best_text.strip():
            return False, "", "No text could be extracted. Try a clearer image."

        return True, best_text, ""

    except Exception as e:
        return False, "", f"OCR processing error: {str(e)}"


def parse_medicines_from_text(raw_text: str) -> dict:
    """
    Parse extracted OCR text to identify medicine-related lines.
    Returns a structured dict with:
      - highlighted_lines: lines likely containing medicine info
      - detected_medicines: known medicine names found
      - dosages: dosage patterns found
      - full_text: cleaned full text
    """
    lines = raw_text.splitlines()
    cleaned_lines = [l.strip() for l in lines if l.strip()]

    highlighted = []
    detected_medicines = []
    dosages = []

    # Regex patterns
    dosage_pattern = re.compile(
        r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|iu|units?)\b", re.IGNORECASE
    )
    frequency_pattern = re.compile(
        r"\b(once|twice|thrice|1|2|3|4)\s*(?:times?)?\s*"
        r"(?:a\s*)?(?:day|daily|weekly|hourly|hours?)\b",
        re.IGNORECASE,
    )

    for line in cleaned_lines:
        line_lower = line.lower()
        is_medicine_line = False

        # Check for known medicine names
        for med in COMMON_MEDICINES:
            if med in line_lower:
                if med not in detected_medicines:
                    detected_medicines.append(med.title())
                is_medicine_line = True

        # Check for dosage patterns
        dose_matches = dosage_pattern.findall(line)
        if dose_matches:
            for val, unit in dose_matches:
                dosages.append(f"{val} {unit.lower()}")
            is_medicine_line = True

        # Check for keywords
        if any(kw in line_lower for kw in MEDICINE_KEYWORDS):
            is_medicine_line = True

        # Check for frequency patterns
        if frequency_pattern.search(line):
            is_medicine_line = True

        if is_medicine_line and len(line) > 3:
            highlighted.append(line)

    return {
        "highlighted_lines": highlighted,
        "detected_medicines": list(set(detected_medicines)),
        "dosages": list(set(dosages)),
        "full_text": "\n".join(cleaned_lines),
        "line_count": len(cleaned_lines),
    }


def process_prescription(image_bytes: bytes) -> dict:
    """
    Full pipeline: OCR → parse → return structured result.
    """
    success, raw_text, error = extract_text_from_image(image_bytes)
    if not success:
        return {
            "success": False,
            "error": error,
            "raw_text": "",
            "parsed": {},
        }

    parsed = parse_medicines_from_text(raw_text)
    return {
        "success": True,
        "error": "",
        "raw_text": raw_text,
        "parsed": parsed,
    }

