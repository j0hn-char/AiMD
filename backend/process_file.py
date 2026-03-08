import pdfplumber
import io
import base64

def process_file(contents: bytes, filename: str) -> dict:
  
    
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        text = ""
        
        try:
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            return {"type": "error", "data": f"Δεν μπόρεσα να ανοίξω το PDF: {str(e)}"}

        # Αν δεν βγήκε καθόλου text (σαρωμένο PDF)
        if len(text.strip()) < 50:
            return {"type": "error", "data": "Δεν μπόρεσα να εξάγω κείμενο. Δοκίμασε πιο καθαρό αρχείο."}

        return {
            "type": "text",
            "data": text,
            "format": "pdf"
        }

    # ─── JPEG / PNG ───
    elif ext in ["jpg", "jpeg", "png"]:
        
        try:
            image_base64 = base64.standard_b64encode(contents).decode("utf-8")
        except Exception as e:
            return {"type": "error", "data": f"Δεν μπόρεσα να επεξεργαστώ την εικόνα: {str(e)}"}

        media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"

        return {
            "type": "image",
            "data": image_base64,
            "media_type": media_type,
            "format": ext
        }

    # ─── Μη υποστηριζόμενος τύπος ───
    else:
        return {
            "type": "error",
            "data": f"Μη υποστηριζόμενος τύπος αρχείου: .{ext} — Αποδεκτοί τύποι: PDF, JPG, PNG"
        }