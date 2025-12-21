import pandas as pd
import re
import os


# Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ocr_raw_text.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "ocr_cleaned_text.csv")


# OCR CLEANING FUNCTION
def clean_ocr_text(text):
    if pd.isna(text):
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove URLs / file artifacts
    text = re.sub(r"http\S+|www\S+", " ", text)

    # 3. Remove OCR junk symbols
    text = re.sub(r"[|_=<>*/#~^]", " ", text)

    # 4. Remove brackets & quotes
    text = re.sub(r"[{}\[\]\"']", " ", text)

    # 5. Remove known OCR garbage words
    garbage_words = [
        "ee", "ra", "ga", "ds", "md", "dr",
        "computerised", "pathologic", "diagnostic",
        "hospital", "laboratory", "centre", "time",
        "report release", "sample id"
    ]
    for word in garbage_words:
        text = re.sub(rf"\b{word}\b", " ", text)

    # 6. Keep only medical-safe characters
    text = re.sub(r"[^a-z0-9.%/()\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()



    # 7. Remove extra spaces
    text = " ".join(text.split())

    return text

# Load OCR raw text
df = pd.read_csv(INPUT_FILE)

# Apply cleaning
df["clean_text"] = df["raw_text"].apply(clean_ocr_text)

# Save cleaned text
df.to_csv(OUTPUT_FILE, index=False)

print(" OCR text cleaned successfully")
print(f"Saved to: {OUTPUT_FILE}")

# sample output
print("\n SAMPLE CLEANED TEXT:")
print(df["clean_text"].iloc[0][:])
print("\n===== CLEAN_TEXT ONLY =====\n")
print(df["clean_text"].iloc[0])

df = pd.read_csv("data/processed/ocr_cleaned_text.csv")

sample = df["clean_text"].iloc[0]
print(sample)
print("Has double spaces:", "  " in sample)

