import os
import cv2
import pytesseract
import pandas as pd

# Set Tesseract path (Windows)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Resolve base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
IMAGE_DIR = os.path.join(RAW_DIR, "lbmaske")

print("BASE_DIR:", BASE_DIR)
print("IMAGE_DIR:", IMAGE_DIR)
print("IMAGE_DIR exists?", os.path.exists(IMAGE_DIR))

if not os.path.exists(IMAGE_DIR):
    raise FileNotFoundError(f"Image directory not found: {IMAGE_DIR}")

# OCR Extraction
rows = []

for img_name in os.listdir(IMAGE_DIR):
    if img_name.lower().endswith((".png", ".jpg", ".jpeg")):
        print(f"Processing image: {img_name}")
        img_path = os.path.join(IMAGE_DIR, img_name)

        img = cv2.imread(img_path)
        if img is None:
            print(f" Could not read image: {img_name}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to binarize the image (improves OCR accuracy)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # --psm 6 assumes a single uniform block of text, which is better for lists/tables
        text = pytesseract.image_to_string(gray, config='--psm 6')

        rows.append({
            "image_name": img_name,
            "raw_text": text
        })


# Save OCR output
ocr_df = pd.DataFrame(rows)

OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "ocr_raw_text.csv")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

ocr_df.to_csv(OUTPUT_PATH, index=False)

print(" OCR completed successfully")
print("Saved to:", OUTPUT_PATH)