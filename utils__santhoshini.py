# utils.py
import re

def mock_ocr_pipeline(file_path):
    """
    Simulates the 'Input Interface & Parser' and 'Data Extraction Engine'.
    In a real deployment, you would import 'pytesseract' here.
    """
    # Mocking extracted text for demonstration
    return {
        "hemoglobin": 11.0,       # Anemic
        "glucose_fasting": 135,   # High
        "cholesterol_total": 210, # Borderline
        "hdl": 38,                # Low
        "ldl": 140,               # High
        "creatinine": 1.2         # Normal
    }

def validate_and_standardize(data):
    """
    Implements 'Data Validation & Standardization Module'.
    Ensures biological plausibility and cleans data.
    """
    clean_data = {}
    errors = []

    # 1. Biological Limits Check (Sanity Check)
    limits = {
        "hemoglobin": (2, 25), # Values outside this are likely OCR errors
        "glucose_fasting": (20, 1000),
        "cholesterol_total": (50, 500)
    }

    for param, value in data.items():
        # Type Conversion
        try:
            val = float(value)
        except ValueError:
            errors.append(f"Invalid format for {param}")
            continue

        # Range Check (Plausibility)
        if param in limits:
            min_v, max_v = limits[param]
            if not (min_v <= val <= max_v):
                errors.append(f"Implausible value for {param}: {val}")
                continue
        
        clean_data[param] = val

    return clean_data, errors