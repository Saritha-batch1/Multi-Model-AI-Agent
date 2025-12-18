def extract_text(path: str) -> str:
    import os, re
    import pdfplumber
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    # ---- WINDOWS ONLY ----
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    text_out = []

    # ---------------- IMAGE ----------------
    if ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        img = Image.open(path)
        text_out.append(pytesseract.image_to_string(img))

    # ---------------- PDF ------------------
    elif ext == ".pdf":
        try:
            with pdfplumber.open(path) as pdf:
                is_text_pdf = False

                # Detect text-based PDF (first 2 pages)
                for page in pdf.pages[:2]:
                    t = page.extract_text()
                    if t and len(t.strip()) > 20:
                        is_text_pdf = True
                        break

                # ---- TEXT PDF (with OCR fallback per page) ----
                if is_text_pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text_out.append(t)
                        else:
                            img = page.to_image(resolution=200).original
                            text_out.append(pytesseract.image_to_string(img))

                # ---- SCANNED PDF ----
                else:
                    images = convert_from_path(path, dpi=200)
                    for img in images:
                        text_out.append(pytesseract.image_to_string(img))

        except Exception as e:
            raise RuntimeError(f"PDF processing failed: {e}")

    else:
        raise ValueError("Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP")

    # ---------------- NORMALIZATION ----------------
    text = "\n".join(text_out).lower()
    text = text.translate(str.maketrans({
        "–": "-", "—": "-", "−": "-",
        "×": "x", "X": "x"
    }))
    text = re.sub(r"[^\x00-\x7f]", " ", text)
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()

