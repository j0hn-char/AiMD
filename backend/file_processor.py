"""
fileprocessor.py
────────────────
Επεξεργάζεται αρχεία που ανεβάζει ο χρήστης.

Υποστηριζόμενοι τύποι:
  • PDF        → εξαγωγή κειμένου με pdfplumber
  • JPG / PNG  → base64 encoding για vision APIs
  • DCM        → DICOM (τομογραφίες/μαγνητικές) → PNG → base64

process_files() δέχεται λίστα αρχείων και επιστρέφει:
  {
    "texts":  ["extracted text από PDFs..."],   # συνενωμένο κείμενο
    "images": [                                  # λίστα εικόνων για vision
      { "data": "base64...", "media_type": "image/png" },
      ...
    ],
    "errors": ["μήνυμα λάθους αν κάποιο αρχείο απέτυχε"]
  }
"""

import pdfplumber
import io
import base64


# ── DICOM import (προαιρετικό — εγκατάσταση: pip install pydicom Pillow) ──────
try:
    import pydicom
    from PIL import Image as PILImage
    import numpy as np
    DICOM_SUPPORTED = True
except ImportError:
    DICOM_SUPPORTED = False


# ── Single file processor ─────────────────────────────────────────────────────

def process_file(contents: bytes, filename: str) -> dict:
    """
    Επεξεργάζεται ένα αρχείο και επιστρέφει dict με τον τύπο και τα δεδομένα.

    Επιστρέφει:
      { "type": "text",  "data": "...",    "format": "pdf" }
      { "type": "image", "data": base64,   "media_type": "image/jpeg" }
      { "type": "error", "data": "μήνυμα" }
    """
    ext = filename.lower().split(".")[-1]

    # ── PDF ──────────────────────────────────────────────────────────────────
    if ext == "pdf":
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            return {"type": "error", "data": f"Δεν μπόρεσα να ανοίξω το PDF '{filename}': {str(e)}"}

        if len(text.strip()) < 50:
            return {"type": "error", "data": f"Δεν μπόρεσα να εξάγω κείμενο από το '{filename}'. Δοκίμασε πιο καθαρό αρχείο."}

        return {"type": "text", "data": text, "format": "pdf"}

    # ── JPEG / PNG ────────────────────────────────────────────────────────────
    elif ext in ["jpg", "jpeg", "png"]:
        try:
            image_base64 = base64.standard_b64encode(contents).decode("utf-8")
        except Exception as e:
            return {"type": "error", "data": f"Δεν μπόρεσα να επεξεργαστώ την εικόνα '{filename}': {str(e)}"}

        media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        return {"type": "image", "data": image_base64, "media_type": media_type, "format": ext}

    # ── DICOM (τομογραφίες / μαγνητικές) ─────────────────────────────────────
    elif ext == "dcm":
        if not DICOM_SUPPORTED:
            return {
                "type": "error",
                "data": "Το DICOM δεν υποστηρίζεται. Εγκατάστησε: pip install pydicom Pillow numpy"
            }
        return _process_dicom(contents, filename)

    # ── Μη υποστηριζόμενος τύπος ─────────────────────────────────────────────
    else:
        return {
            "type": "error",
            "data": f"Μη υποστηριζόμενος τύπος αρχείου: .{ext} — Αποδεκτοί τύποι: PDF, JPG, PNG, DCM"
        }


def _process_dicom(contents: bytes, filename: str) -> dict:
    """
    Μετατρέπει DICOM αρχείο σε PNG και επιστρέφει base64.
    Χειρίζεται normalization για σωστή απεικόνιση.
    """
    try:
        dicom_file = pydicom.dcmread(io.BytesIO(contents))
        pixel_array = dicom_file.pixel_array.astype(float)

        # Normalization → 0-255 για σωστή απεικόνιση
        pixel_min = pixel_array.min()
        pixel_max = pixel_array.max()

        if pixel_max > pixel_min:
            pixel_array = (pixel_array - pixel_min) / (pixel_max - pixel_min) * 255.0
        else:
            pixel_array = np.zeros_like(pixel_array)

        pixel_array = pixel_array.astype(np.uint8)

        # Grayscale → RGB (τα vision APIs χρειάζονται RGB)
        pil_image = PILImage.fromarray(pixel_array)
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Αποθήκευση ως PNG σε memory
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)

        image_base64 = base64.standard_b64encode(buffer.read()).decode("utf-8")

        return {
            "type":       "image",
            "data":       image_base64,
            "media_type": "image/png",
            "format":     "dcm"
        }

    except Exception as e:
        return {"type": "error", "data": f"Δεν μπόρεσα να επεξεργαστώ το DICOM '{filename}': {str(e)}"}


# ── Multi-file processor ──────────────────────────────────────────────────────

def process_files(files: list[tuple[bytes, str]]) -> dict:
    """
    Επεξεργάζεται λίστα αρχείων και επιστρέφει συγκεντρωτικό αποτέλεσμα.

    files = [ (contents_bytes, filename), ... ]

    Επιστρέφει:
    {
        "texts":  ["κείμενο από PDF 1", "κείμενο από PDF 2"],
        "images": [
            { "data": "base64...", "media_type": "image/png",  "filename": "xray.dcm" },
            { "data": "base64...", "media_type": "image/jpeg", "filename": "scan.jpg" },
        ],
        "errors": ["μήνυμα λάθους αν κάποιο αρχείο απέτυχε"]
    }
    """
    texts  = []
    images = []
    errors = []

    for contents, filename in files:
        result = process_file(contents, filename)

        if result["type"] == "text":
            # Προσθέτουμε το όνομα αρχείου ως header για context
            texts.append(f"=== {filename} ===\n{result['data']}")

        elif result["type"] == "image":
            images.append({
                "data":       result["data"],
                "media_type": result["media_type"],
                "filename":   filename
            })

        elif result["type"] == "error":
            errors.append(result["data"])

    return {
        "texts":  texts,
        "images": images,
        "errors": errors
    }