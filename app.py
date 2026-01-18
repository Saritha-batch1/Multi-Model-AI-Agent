"""
Multi-Model AI Agent for Automated Health Diagnostics
Production-Ready Application with Enhanced PDF & Twin Red Buttons

CRITICAL FIXES:
- JSON Mode enabled for Groq API (response_format={"type": "json_object"})
- Robust JSON parsing with error recovery
- max_tokens=8000 for large PDF handling (19+ pages)
- generate_health_recommendations function included
- Twin red button styling for consistency

Features:
- Universal report ingestion (PDF, Images, JSON)
- AI-powered data extraction using Groq LLM (JSON Mode)
- Medical analysis engine with 30+ blood parameters
- Cardiovascular risk assessment
- Enhanced PDF report generation with color-coded tables
- Cloud data persistence with Supabase
- Red pill style sidebar navigation
- Twin red button styling
"""

# ============================================================================
# IMPORTS & CONFIGURATION
# ============================================================================

import streamlit as st
import json
import os
import pandas as pd
import re
from pathlib import Path
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# TESSERACT CONFIGURATION FOR WINDOWS
# ============================================================================

try:
    import pytesseract
    OCR_AVAILABLE = True
    
    # Configure Tesseract path for Windows
    tesseract_path = os.getenv("TESSERACT_PATH")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
except ImportError:
    OCR_AVAILABLE = False

# ============================================================================
# OPTIONAL LIBRARY IMPORTS
# ============================================================================

try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = "PyPDF2"
    except ImportError:
        PDF_LIBRARY = None

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION (MUST BE FIRST STREAMLIT COMMAND)
# ============================================================================

st.set_page_config(
    page_title="🏥 Health Diagnostics AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MODERN CSS STYLING - RED PILL NAVIGATION & TWIN RED BUTTONS
# ============================================================================

st.markdown("""
    <style>
    /* ===== GLOBAL RESET ===== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ===== MAIN APP BACKGROUND - PREMIUM GRADIENT ===== */
    .stApp {
        background: linear-gradient(to right, #ece9e6, #ffffff) !important;
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    .main {
        background: transparent !important;
    }
    
    /* ===== FORCE ALL TEXT TO DARK GREY BY DEFAULT ===== */
    .stApp {
        color: #333333 !important;
    }
    
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp span, .stApp label, .stApp li, .stApp a, .stApp strong, .stApp em {
        color: #333333 !important;
    }
    
    .stMarkdown {
        color: #333333 !important;
    }
    
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMarkdown span, .stMarkdown label, .stMarkdown li, .stMarkdown a, .stMarkdown strong, .stMarkdown em {
        color: #333333 !important;
    }
    
    /* ===== SIDEBAR STYLING - CLEAN WHITE ===== */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E0E0E0 !important;
    }
    
    /* Force all sidebar text to DARK GREY */
    [data-testid="stSidebar"] {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] em {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #333333 !important;
    }
    
    /* ===== RED PILL NAVIGATION STYLING ===== */
    /* Hide the radio circles */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
    /* Style radio labels as navigation items */
    div[role="radiogroup"] label {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        display: block !important;
        width: 100% !important;
    }
    
    /* Hover effect - light grey background */
    div[role="radiogroup"] label:hover {
        background-color: #F5F5F5 !important;
        transform: translateX(4px) !important;
    }
    
    /* Active/checked state - RED PILL (#FF4B4B) with white text */
    div[role="radiogroup"] label:has(input:checked) {
        background: #FF4B4B !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    
    /* Hide the actual radio input */
    div[role="radiogroup"] input[type="radio"] {
        display: none !important;
    }
    
    /* ===== TWIN RED BUTTONS - STANDARDIZED STYLING ===== */
    /* Target both regular buttons and download buttons */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #FF4B4B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2) !important;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #E63946 !important;
        box-shadow: 0 6px 16px rgba(255, 75, 75, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* ===== METRIC CARDS - GLASSMORPHISM ===== */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-left: 4px solid #FF4B4B !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25) !important;
    }
    
    [data-testid="metric-container"] * {
        color: #333333 !important;
    }
    
    /* ===== TABS - MODERN STYLE ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
        color: #333333 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #FF4B4B !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
    }
    
    /* ===== DATAFRAME - GLASSMORPHISM ===== */
    [data-testid="stDataFrame"] {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* ===== TEXT INPUT & TEXTAREA - MODERN ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #333333 !important;
        border: 2px solid rgba(255, 75, 75, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FF4B4B !important;
        box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #999999 !important;
    }
    
    /* ===== FILE UPLOADER - MODERN ===== */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 2px dashed rgba(255, 75, 75, 0.3) !important;
    }
    
    /* ===== ALERT BOXES - GLASSMORPHISM ===== */
    .stAlert {
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
    }
    
    .stSuccess {
        background-color: rgba(212, 237, 218, 0.95) !important;
        border-left: 4px solid #28a745 !important;
    }
    
    .stError {
        background-color: rgba(248, 215, 218, 0.95) !important;
        border-left: 4px solid #dc3545 !important;
    }
    
    .stWarning {
        background-color: rgba(255, 243, 205, 0.95) !important;
        border-left: 4px solid #ffc107 !important;
    }
    
    .stInfo {
        background-color: rgba(209, 236, 241, 0.95) !important;
        border-left: 4px solid #17a2b8 !important;
    }
    
    /* ===== CUSTOM PREMIUM CARD ===== */
    .premium-card {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #FF4B4B !important;
        transition: all 0.3s ease !important;
    }
    
    .premium-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25) !important;
    }
    
    .premium-card h3 {
        color: #333333 !important;
        margin-bottom: 1rem !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    
    .premium-card p {
        color: #333333 !important;
        line-height: 1.6 !important;
    }
    
    /* ===== HERO CARD - LANDING PAGE ===== */
    .hero-card {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 60px 40px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        text-align: center !important;
        margin: 2rem auto !important;
        max-width: 600px !important;
    }
    
    .hero-card h1 {
        color: #333333 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
    }
    
    .hero-card .hero-icon {
        font-size: 4rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    .hero-card .hero-subtitle {
        color: #666666 !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
        line-height: 1.6 !important;
    }
    
    .hero-card .feature-list {
        text-align: left !important;
        display: inline-block !important;
        margin-top: 2rem !important;
    }
    
    .hero-card .feature-item {
        color: #333333 !important;
        font-size: 1rem !important;
        margin: 0.8rem 0 !important;
        line-height: 1.5 !important;
    }
    
    /* ===== HEADERS - MODERN TYPOGRAPHY ===== */
    .main-header {
        font-size: 2.8rem !important;
        color: #333333 !important;
        margin-bottom: 0.5rem !important;
        font-weight: 800 !important;
        text-align: center !important;
    }
    
    .sub-header {
        font-size: 1.2rem !important;
        color: #666666 !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
        font-weight: 500 !important;
    }
    
    .section-header {
        font-size: 1.5rem !important;
        color: #333333 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #FF4B4B !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* ===== STATUS BADGES - MODERN PILLS ===== */
    .badge-normal {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        color: #155724 !important;
        padding: 0.4rem 1rem !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2) !important;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        color: #721c24 !important;
        padding: 0.4rem 1rem !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2) !important;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        color: #856404 !important;
        padding: 0.4rem 1rem !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        display: inline-block !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2) !important;
    }
    
    /* ===== RISK CARDS - MODERN ===== */
    .risk-card {
        padding: 1.5rem !important;
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border-left: 4px solid #FF4B4B !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        margin: 0.5rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .risk-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25) !important;
    }
    
    .risk-card strong {
        color: #333333 !important;
        font-size: 1.1rem !important;
    }
    
    .risk-card small {
        color: #666666 !important;
    }
    
    /* ===== EXPANDER - MODERN ===== */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: #333333 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 1) !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2) !important;
    }
    
    /* ===== SMOOTH SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF4B4B 100%);
    }
    
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# REFERENCE RANGES - STANDARDIZED TO ABSOLUTE NUMBERS
# ============================================================================

REFERENCE_RANGES = {
    "glucose": {"name": "Glucose (Fasting)", "display_unit": "mg/dL", "normal_range": (70, 100), "category": "Glucose Metabolism"},
    "glucose_random": {"name": "Glucose (Random)", "display_unit": "mg/dL", "normal_range": (70, 140), "category": "Glucose Metabolism"},
    "hba1c": {"name": "HbA1c", "display_unit": "%", "normal_range": (0, 5.7), "category": "Glucose Metabolism"},
    "hemoglobin": {"name": "Hemoglobin", "display_unit": "g/dL", "normal_range": (12.0, 17.5), "category": "Red Blood Cells"},
    "hematocrit": {"name": "Hematocrit", "display_unit": "%", "normal_range": (36, 46), "category": "Red Blood Cells"},
    "rbc": {"name": "Red Blood Cell Count", "display_unit": "million/µL", "normal_range": (4000000, 6000000), "category": "Red Blood Cells"},
    "mcv": {"name": "Mean Corpuscular Volume", "display_unit": "fL", "normal_range": (80, 100), "category": "Red Blood Cells"},
    "mch": {"name": "Mean Corpuscular Hemoglobin", "display_unit": "pg", "normal_range": (27, 33), "category": "Red Blood Cells"},
    "mchc": {"name": "Mean Corpuscular Hemoglobin Concentration", "display_unit": "g/dL", "normal_range": (32, 36), "category": "Red Blood Cells"},
    "wbc": {"name": "White Blood Cell Count", "display_unit": "cells/µL", "normal_range": (4000, 11000), "category": "White Blood Cells"},
    "neutrophils": {"name": "Neutrophils", "display_unit": "%", "normal_range": (50, 70), "category": "White Blood Cells"},
    "lymphocytes": {"name": "Lymphocytes", "display_unit": "%", "normal_range": (20, 40), "category": "White Blood Cells"},
    "monocytes": {"name": "Monocytes", "display_unit": "%", "normal_range": (2, 8), "category": "White Blood Cells"},
    "eosinophils": {"name": "Eosinophils", "display_unit": "%", "normal_range": (1, 4), "category": "White Blood Cells"},
    "basophils": {"name": "Basophils", "display_unit": "%", "normal_range": (0, 1), "category": "White Blood Cells"},
    "platelets": {"name": "Platelet Count", "display_unit": "cells/µL", "normal_range": (150000, 450000), "category": "Platelets"},
    "total_cholesterol": {"name": "Total Cholesterol", "display_unit": "mg/dL", "normal_range": (0, 200), "category": "Lipid Panel"},
    "hdl": {"name": "HDL Cholesterol", "display_unit": "mg/dL", "normal_range": (40, 300), "category": "Lipid Panel"},
    "ldl": {"name": "LDL Cholesterol", "display_unit": "mg/dL", "normal_range": (0, 100), "category": "Lipid Panel"},
    "triglycerides": {"name": "Triglycerides", "display_unit": "mg/dL", "normal_range": (0, 150), "category": "Lipid Panel"},
    "ast": {"name": "AST (Aspartate Aminotransferase)", "display_unit": "U/L", "normal_range": (10, 40), "category": "Liver Function"},
    "alt": {"name": "ALT (Alanine Aminotransferase)", "display_unit": "U/L", "normal_range": (7, 56), "category": "Liver Function"},
    "alkaline_phosphatase": {"name": "Alkaline Phosphatase", "display_unit": "U/L", "normal_range": (30, 120), "category": "Liver Function"},
    "bilirubin": {"name": "Total Bilirubin", "display_unit": "mg/dL", "normal_range": (0.1, 1.2), "category": "Liver Function"},
    "creatinine": {"name": "Creatinine", "display_unit": "mg/dL", "normal_range": (0.7, 1.3), "category": "Kidney Function"},
    "bun": {"name": "Blood Urea Nitrogen", "display_unit": "mg/dL", "normal_range": (7, 20), "category": "Kidney Function"},
    "sodium": {"name": "Sodium", "display_unit": "mEq/L", "normal_range": (136, 145), "category": "Electrolytes"},
    "potassium": {"name": "Potassium", "display_unit": "mEq/L", "normal_range": (3.5, 5.0), "category": "Electrolytes"},
    "chloride": {"name": "Chloride", "display_unit": "mEq/L", "normal_range": (98, 107), "category": "Electrolytes"},
    "iron": {"name": "Serum Iron", "display_unit": "µg/dL", "normal_range": (60, 170), "category": "Iron Metabolism"},
    "ferritin": {"name": "Ferritin", "display_unit": "ng/mL", "normal_range": (30, 300), "category": "Iron Metabolism"},
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_value_with_unit_conversion(value, unit, param_key):
    """Normalize a value to absolute numbers using standardized conversion logic."""
    if param_key not in REFERENCE_RANGES or value is None:
        return value, ""
    
    try:
        value = float(value)
        unit_lower = unit.lower().strip()
        
        if "lakh" in unit_lower:
            return value * 100000, f"(converted from {unit})"
        if "million" in unit_lower:
            return value * 1000000, f"(converted from {unit})"
        if "thousand" in unit_lower or unit_lower.endswith("k") or "/k" in unit_lower:
            return value * 1000, f"(converted from {unit})"
        if param_key in ["wbc", "platelets"] and value < 50:
            return value * 1000, f"(assumed thousands)"
        
        return value, ""
    except (ValueError, TypeError):
        return value, ""


def get_parameter_status(normalized_value, param_key):
    """Determine if a normalized value is Normal, High, or Low."""
    if param_key not in REFERENCE_RANGES or normalized_value is None:
        return "Unknown"
    
    try:
        normalized_value = float(normalized_value)
        min_val, max_val = REFERENCE_RANGES[param_key]["normal_range"]
        
        if normalized_value < min_val:
            return "Low"
        elif normalized_value > max_val:
            return "High"
        else:
            return "Normal"
    except (ValueError, TypeError):
        return "Unknown"


def initialize_supabase():
    """Initialize Supabase client using credentials from environment (prioritizes .env)."""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url and "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        if not key and "SUPABASE_KEY" in st.secrets:
            key = st.secrets["SUPABASE_KEY"]
        
        if not url or not key:
            return None
        
        client = create_client(url, key)
        return client
    except Exception as e:
        st.warning(f"Failed to initialize Supabase: {str(e)}")
        return None


def save_report_to_db(user_id, file_name, extracted_json, user_context):
    """Save extracted blood report data to Supabase database."""
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Supabase library is not installed"}
    
    try:
        supabase = initialize_supabase()
        
        if not supabase:
            return {"status": "error", "message": "Supabase credentials not configured"}
        
        report_data = {
            "user_id": user_id,
            "file_name": file_name,
            "extracted_data": extracted_json,
            "user_context": user_context,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("blood_reports").insert(report_data).execute()
        
        return {"status": "success", "message": "Report saved to database successfully", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save report: {str(e)}"}


def repair_json_string(json_str):
    """Attempt to repair common JSON formatting issues."""
    try:
        # Try to parse as-is first
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Try to fix numbered list items (0:{...}, 1:{...}) to proper array format
    try:
        # Replace numbered keys with array format
        fixed = re.sub(r'(\d+):\s*{', '{', json_str)
        # Remove trailing commas before closing braces
        fixed = re.sub(r',\s*}', '}', fixed)
        fixed = re.sub(r',\s*]', ']', fixed)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    
    return None


def parse_report_with_llm(raw_text, api_key, user_context=""):
    """Process extracted text using Groq LLM to structure blood test data.
    
    CRITICAL FIXES:
    - JSON Mode enabled (response_format={"type": "json_object"})
    - max_tokens=8000 for large PDFs (19+ pages)
    - Robust JSON parsing with error recovery
    """
    if not GROQ_AVAILABLE:
        return {"status": "error", "message": "Groq library is not installed"}
    
    if not api_key or api_key.strip() == "":
        return {"status": "error", "message": "Groq API key is required"}
    
    try:
        client = Groq(api_key=api_key)
        
        system_prompt = """You are an expert medical data extraction assistant. Extract all blood test parameters from the provided text.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON object (no markdown, no extra text)
2. Use standard JSON list format for parameters: [{"name": "...", "value": ..., "unit": "..."}, ...]
3. Do NOT number the items in the parameters list (no "0:{...}", "1:{...}")
4. Ensure all JSON is properly formatted with correct commas and brackets

Return this exact JSON structure:
{
    "report_metadata": {"extraction_date": "YYYY-MM-DD", "total_parameters": number, "user_context": "user's symptom/reason"},
    "parameters": [{"name": "Parameter Name", "value": numeric_value, "unit": "Unit", "reference_range": "min-max", "status": "Normal/High/Low", "clinical_significance": "Brief explanation"}],
    "summary": "Brief summary of findings",
    "context_based_insights": "Specific insights based on user's symptoms"
}"""
        
        context_note = f"\nUser's Context: {user_context}" if user_context else ""
        user_message = f"""Please analyze this blood test report and extract all parameters into structured JSON format:

{raw_text}{context_note}

Remember: Return ONLY valid JSON, no additional text. Use standard array format for parameters list."""
        
        # CRITICAL FIX: JSON Mode enabled + max_tokens=8000
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=8000,
            response_format={"type": "json_object"},  # CRITICAL: Force JSON output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        response_text = message.choices[0].message.content.strip()
        
        try:
            # Try direct JSON parsing first
            structured_data = json.loads(response_text)
            return {"status": "success", "message": "Report analyzed successfully", "data": structured_data}
        except json.JSONDecodeError as e:
            # Try to repair JSON
            repaired = repair_json_string(response_text)
            if repaired:
                return {"status": "success", "message": "Report analyzed successfully (repaired JSON)", "data": repaired}
            
            # If repair fails, return error with raw response for debugging
            return {"status": "error", "message": f"Failed to parse LLM response: {str(e)}", "raw_response": response_text[:500]}
    except Exception as e:
        return {"status": "error", "message": f"LLM processing failed: {str(e)}"}


def analyze_blood_data(extracted_json):
    """Analyze blood test data with strict standardization to absolute numbers."""
    analysis = {
        "parameters": [],
        "risk_scores": {},
        "summary": extracted_json.get("summary", ""),
        "warnings": [],
        "abnormal_findings": []
    }
    
    parameters = extracted_json.get("parameters", [])
    
    for param in parameters:
        name = param.get("name", "").lower()
        value = param.get("value")
        unit = param.get("unit", "")
        
        matched_key = None
        for ref_key in REFERENCE_RANGES.keys():
            if ref_key in name or name in ref_key:
                matched_key = ref_key
                break
        
        if not matched_key:
            analysis["parameters"].append({
                "name": param.get("name", ""),
                "value": value,
                "unit": unit,
                "normalized_value": value,
                "status": "Unknown",
                "reference_range": "N/A",
                "display_range": "N/A",
                "category": "Other"
            })
            continue
        
        normalized_value, conversion_note = normalize_value_with_unit_conversion(value, unit, matched_key)
        status = get_parameter_status(normalized_value, matched_key)
        ref_range = REFERENCE_RANGES[matched_key]["normal_range"]
        display_unit = REFERENCE_RANGES[matched_key]["display_unit"]
        category = REFERENCE_RANGES[matched_key]["category"]
        
        analysis["parameters"].append({
            "name": param.get("name", ""),
            "value": value,
            "unit": unit,
            "normalized_value": normalized_value,
            "status": status,
            "reference_range": ref_range,
            "display_range": f"{int(ref_range[0])} - {int(ref_range[1])}",
            "display_unit": display_unit,
            "category": category,
            "conversion_note": conversion_note
        })
        
        if status in ["High", "Low"]:
            warning_msg = f"{param.get('name', 'Unknown')}: {status} ({normalized_value} {display_unit})"
            analysis["warnings"].append(warning_msg)
            analysis["abnormal_findings"].append({
                "parameter": param.get("name", ""),
                "status": status,
                "normalized_value": normalized_value,
                "display_unit": display_unit,
                "reference_range": ref_range
            })
    
    return analysis


def calculate_heart_risk(analysis_results):
    """Calculate cardiovascular health risk based on lipid panel values."""
    heart_risk = {
        "has_data": False,
        "total_cholesterol": None,
        "hdl": None,
        "ldl": None,
        "cholesterol_hdl_ratio": None,
        "non_hdl_cholesterol": None,
        "risk_level": None,
        "risk_color": None,
        "recommendation": None
    }
    
    parameters = analysis_results.get("parameters", [])
    
    for param in parameters:
        name_lower = param.get("name", "").lower()
        value = param.get("normalized_value")
        
        if "total cholesterol" in name_lower:
            heart_risk["total_cholesterol"] = value
        elif "hdl" in name_lower and "cholesterol" in name_lower:
            heart_risk["hdl"] = value
        elif "ldl" in name_lower and "cholesterol" in name_lower:
            heart_risk["ldl"] = value
    
    if heart_risk["total_cholesterol"] and heart_risk["hdl"]:
        try:
            total_chol = float(heart_risk["total_cholesterol"])
            hdl = float(heart_risk["hdl"])
            
            heart_risk["cholesterol_hdl_ratio"] = round(total_chol / hdl, 2)
            heart_risk["non_hdl_cholesterol"] = round(total_chol - hdl, 2)
            
            ratio = heart_risk["cholesterol_hdl_ratio"]
            
            if ratio < 3.5:
                heart_risk["risk_level"] = "Optimal Risk"
                heart_risk["risk_color"] = "#28a745"
                heart_risk["recommendation"] = "Excellent lipid profile. Maintain current lifestyle and diet."
            elif ratio <= 5.0:
                heart_risk["risk_level"] = "Moderate Risk"
                heart_risk["risk_color"] = "#ffc107"
                heart_risk["recommendation"] = "Consider lifestyle modifications: increase exercise, reduce saturated fats."
            else:
                heart_risk["risk_level"] = "High Risk"
                heart_risk["risk_color"] = "#dc3545"
                heart_risk["recommendation"] = "⚠️ Consult a cardiologist regarding lipid management."
            
            heart_risk["has_data"] = True
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    
    return heart_risk


def generate_pdf_report(user_id, analysis_df, heart_risk_data, summary, recommendations):
    """Generate a comprehensive PDF report with color-coded tables and recommendations."""
    if not FPDF_AVAILABLE:
        return None
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # ===== HEADER WITH RED BACKGROUND =====
        pdf.set_fill_color(255, 75, 75)  # Red background
        pdf.set_text_color(255, 255, 255)  # White text
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(0, 12, "Blood Test Analysis Report", ln=True, align="C", fill=True)
        
        # Decorative line
        pdf.set_draw_color(255, 75, 75)
        pdf.set_line_width(1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        
        # Reset text color to black
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(5)
        
        # ===== PATIENT INFORMATION =====
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Patient Information", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"User ID: {user_id}", ln=True)
        pdf.ln(3)
        
        # ===== CLINICAL SUMMARY =====
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Clinical Summary", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, summary if summary else "No summary available")
        pdf.ln(3)
        
        # ===== CARDIOVASCULAR ASSESSMENT =====
        if heart_risk_data.get("has_data"):
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(0, 8, "Cardiovascular Health Assessment", ln=True)
            
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 6, f"Total Cholesterol: {heart_risk_data.get('total_cholesterol', 'N/A')} mg/dL", ln=True)
            pdf.cell(0, 6, f"HDL Cholesterol: {heart_risk_data.get('hdl', 'N/A')} mg/dL", ln=True)
            pdf.cell(0, 6, f"LDL Cholesterol: {heart_risk_data.get('ldl', 'N/A')} mg/dL", ln=True)
            pdf.cell(0, 6, f"Cholesterol/HDL Ratio: {heart_risk_data.get('cholesterol_hdl_ratio', 'N/A')}", ln=True)
            pdf.cell(0, 6, f"Risk Level: {heart_risk_data.get('risk_level', 'N/A')}", ln=True)
            pdf.ln(3)
        
        # ===== BLOOD PARAMETERS TABLE WITH COLOR CODING =====
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Blood Parameters", ln=True)
        
        pdf.set_font("Arial", "B", size=9)
        pdf.set_fill_color(255, 75, 75)  # Red header
        pdf.set_text_color(255, 255, 255)  # White text
        pdf.cell(40, 6, "Parameter", border=1, fill=True)
        pdf.cell(25, 6, "Value", border=1, fill=True)
        pdf.cell(25, 6, "Unit", border=1, fill=True)
        pdf.cell(30, 6, "Status", border=1, fill=True)
        pdf.cell(40, 6, "Reference Range", border=1, fill=True, ln=True)
        
        pdf.set_font("Arial", size=8)
        
        for idx, row in analysis_df.iterrows():
            param_name = str(row.get("Parameter", ""))[:35]
            value = str(row.get("Value", ""))[:20]
            unit = str(row.get("Unit", ""))[:20]
            status = str(row.get("Status", ""))[:25]
            ref_range = str(row.get("Reference Range", ""))[:35]
            
            # COLOR CODING: RED for abnormal, BLACK for normal
            if status == "High" or status == "Low":
                pdf.set_text_color(220, 53, 69)  # Red text for abnormal
            else:
                pdf.set_text_color(0, 0, 0)  # Black text for normal
            
            pdf.cell(40, 6, param_name, border=1)
            pdf.cell(25, 6, value, border=1)
            pdf.cell(25, 6, unit, border=1)
            pdf.cell(30, 6, status, border=1)
            pdf.cell(40, 6, ref_range, border=1, ln=True)
        
        pdf.set_text_color(0, 0, 0)  # Reset to black
        pdf.ln(3)
        
        # ===== AI RECOMMENDATIONS SECTION =====
        if recommendations and str(recommendations).strip():
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(0, 8, "AI-Powered Recommendations", ln=True)
            
            pdf.set_font("Arial", size=10)
            # Handle both string and dict recommendations
            if isinstance(recommendations, str):
                pdf.multi_cell(0, 5, recommendations)
            else:
                pdf.multi_cell(0, 5, str(recommendations))
            pdf.ln(3)
        
        # ===== DISCLAIMER =====
        pdf.set_font("Arial", "B", size=10)
        pdf.cell(0, 8, "IMPORTANT DISCLAIMER", ln=True)
        
        pdf.set_font("Arial", size=8)
        disclaimer_text = (
            "This is an AI-generated interpretation based on blood test values and reported symptoms. "
            "It is NOT a medical diagnosis. Please consult a qualified healthcare professional for proper "
            "medical advice, diagnosis, and treatment. Do not delay seeking professional medical care."
        )
        pdf.multi_cell(0, 4, disclaimer_text)
        
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Failed to generate PDF: {str(e)}")
        return None


def extract_text_from_image(image):
    """Extract text from an image using OCR (Tesseract)."""
    if not OCR_AVAILABLE:
        return {"status": "warning", "message": "Tesseract OCR is not installed", "text": None}
    
    try:
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            return {"status": "warning", "message": "No text detected in the image", "text": ""}
        
        return {"status": "success", "message": f"Text extracted successfully ({len(extracted_text)} characters)", "text": extracted_text}
    except Exception as e:
        return {"status": "error", "message": f"OCR extraction failed: {str(e)}", "text": None}


def extract_text_from_pdf(uploaded_file):
    """Extract text from all pages of a PDF file."""
    try:
        if PDF_LIBRARY == "pdfplumber":
            extracted_text = ""
            page_count = 0
            
            with pdfplumber.open(uploaded_file) as pdf:
                page_count = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- Page {page_num} ---\n{page_text}"
            
            if not extracted_text.strip():
                return {"status": "warning", "message": f"PDF loaded but no text found ({page_count} pages)", "text": "", "page_count": page_count}
            
            return {"status": "success", "message": f"Text extracted from {page_count} page(s)", "text": extracted_text, "page_count": page_count}
        else:
            return {"status": "error", "message": "PDF processing library not installed"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to extract text from PDF: {str(e)}"}


def generate_health_recommendations(analysis_results, user_context, api_key):
    """Generate personalized health recommendations based on abnormal findings and user context.
    
    Uses Groq LLM to synthesize insights, dietary recommendations, and next steps.
    """
    if not GROQ_AVAILABLE:
        return {"status": "error", "message": "Groq library is not installed"}
    
    if not api_key or api_key.strip() == "":
        return {"status": "error", "message": "Groq API key is required"}
    
    try:
        # Build context from abnormal findings
        abnormal_params = analysis_results.get("abnormal_findings", [])
        
        # Format abnormal findings for LLM
        abnormal_text = "Abnormal Blood Values Found:\n"
        if not abnormal_params:
            abnormal_text = "All parameters are within normal range."
        else:
            for finding in abnormal_params:
                abnormal_text += f"- {finding['parameter']}: {finding['status']} ({finding['normalized_value']} {finding['display_unit']})\n"
        
        # Build the prompt for LLM
        system_prompt = """You are an empathetic medical AI assistant. Analyze the abnormal blood values in context of the user's reported symptoms.

Provide recommendations in this JSON format:
{
    "insights": "Connection between values and symptoms",
    "dietary": "Dietary & lifestyle advice",
    "next_steps": "Specialist to consult and when"
}

Always include a medical disclaimer."""
        
        user_message = f"""User Symptoms/Context: {user_context if user_context else "Routine checkup"}

{abnormal_text}

Provide personalized recommendations in JSON format."""
        
        # Call Groq API
        client = Groq(api_key=api_key)
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            response_format={"type": "json_object"},  # JSON Mode for consistency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        response_text = message.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            recommendations = json.loads(response_text)
            return {"status": "success", "recommendations": recommendations}
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return {"status": "success", "recommendations": {"insights": response_text}}
    
    except Exception as e:
        return {"status": "error", "message": f"Failed to generate recommendations: {str(e)}"}


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "analyzed_data" not in st.session_state:
    st.session_state["analyzed_data"] = None
if "full_text" not in st.session_state:
    st.session_state["full_text"] = None
if "user_context" not in st.session_state:
    st.session_state["user_context"] = ""
if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None
if "medical_analysis" not in st.session_state:
    st.session_state["medical_analysis"] = None
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = None
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = ""
if "groq_api_key" not in st.session_state:
    st.session_state["groq_api_key"] = ""
if "heart_risk" not in st.session_state:
    st.session_state["heart_risk"] = None

# ============================================================================
# SIDEBAR NAVIGATION (RED PILL STYLE)
# ============================================================================

# Patient ID in Sidebar (Persistent)
st.sidebar.markdown("<h3 style='color: #333333; margin-bottom: 1rem;'>👤 Patient ID</h3>", unsafe_allow_html=True)
patient_id_input = st.sidebar.text_input(
    "Patient ID",
    value=st.session_state.get("patient_id", ""),
    placeholder="Enter patient ID",
    label_visibility="collapsed"
)
if patient_id_input:
    st.session_state["patient_id"] = patient_id_input

st.sidebar.markdown("---")

# Main Navigation (Red Pill Style)
selected_page = st.sidebar.radio(
    "Main Menu",
    ["🏠 Home", "☁️ Upload Report", "⚙️ Settings"],
    label_visibility="collapsed"
)

# ============================================================================
# PAGE 1: HOME (LANDING PAGE)
# ============================================================================

if selected_page == "🏠 Home":
    st.markdown("""
        <div class="hero-card">
            <div class="hero-icon">🏥</div>
            <h1>AI Health Diagnostics Agent</h1>
            <p class="hero-subtitle">Upload your blood report to get instant insights powered by advanced AI analysis</p>
            
            <div class="feature-list">
                <div class="feature-item">✅ Universal Report Support (PDF, Images, JSON)</div>
                <div class="feature-item">✅ AI-Powered Data Extraction</div>
                <div class="feature-item">✅ Medical Analysis with 30+ Parameters</div>
                <div class="feature-item">✅ Cardiovascular Risk Assessment</div>
                <div class="feature-item">✅ Personalized Recommendations</div>
                <div class="feature-item">✅ Professional PDF Reports</div>
                <div class="feature-item">✅ Secure Cloud Storage</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE 2: UPLOAD REPORT (MAIN ANALYSIS)
# ============================================================================

elif selected_page == "☁️ Upload Report":
    st.markdown("<h1 class='main-header'>📋 Blood Report Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood test report and get AI-powered insights</p>", unsafe_allow_html=True)
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload your blood report",
        type=["pdf", "png", "jpg", "jpeg", "json"],
        help="Supported formats: PDF, PNG, JPG, JPEG, JSON"
    )
    
    # User Context Input
    user_context = st.text_area(
        "📝 Tell us about your symptoms or reason for the test",
        placeholder="E.g., 'Feeling fatigued for 2 weeks', 'Routine checkup', 'Suspected diabetes'",
        height=80
    )
    
    if uploaded_file:
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.session_state["user_context"] = user_context
        
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            extraction_result = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            extraction_result = extract_text_from_image(image)
        elif uploaded_file.type == "application/json":
            try:
                json_data = json.load(uploaded_file)
                extraction_result = {"status": "success", "message": "JSON loaded", "text": json.dumps(json_data, indent=2)}
            except:
                extraction_result = {"status": "error", "message": "Invalid JSON file"}
        else:
            extraction_result = {"status": "error", "message": "Unsupported file type"}
        
        if extraction_result["status"] in ["success", "warning"]:
            st.session_state["full_text"] = extraction_result.get("text", "")
            
            # Display extracted text preview
            with st.expander("📄 Extracted Text Preview"):
                st.text_area("Raw extracted text:", value=st.session_state["full_text"], height=200, disabled=True)
        
        # Action Buttons (Twin Red Buttons)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Analyze Report", use_container_width=True):
                if not st.session_state["full_text"]:
                    st.error("❌ No text extracted from the file. Please try another file.")
                else:
                    with st.spinner("🤖 AI is analyzing your report..."):
                        # Get Groq API key from session state or environment
                        groq_api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
                        
                        if not groq_api_key:
                            st.error("❌ Groq API key not configured. Please set it in Settings.")
                        else:
                            # Parse report with LLM (CRITICAL FIX: max_tokens=8000)
                            llm_result = parse_report_with_llm(
                                st.session_state["full_text"],
                                groq_api_key,
                                st.session_state["user_context"]
                            )
                            
                            if llm_result["status"] == "error":
                                st.error(f"❌ LLM Analysis Failed: {llm_result['message']}")
                                if "raw_response" in llm_result:
                                    with st.expander("Debug: Raw LLM Response"):
                                        st.text(llm_result["raw_response"][:500])
                            else:
                                extracted_json = llm_result.get("data", {})
                                
                                # Perform medical analysis
                                medical_analysis = analyze_blood_data(extracted_json)
                                st.session_state["medical_analysis"] = medical_analysis
                                
                                # Calculate heart risk
                                heart_risk = calculate_heart_risk(medical_analysis)
                                st.session_state["heart_risk"] = heart_risk
                                
                                # Generate recommendations
                                with st.spinner("💡 Generating personalized recommendations..."):
                                    recommendations_result = generate_health_recommendations(
                                        medical_analysis,
                                        st.session_state["user_context"],
                                        groq_api_key
                                    )
                                    
                                    if recommendations_result["status"] == "success":
                                        st.session_state["recommendations"] = recommendations_result.get("recommendations", {})
                                    else:
                                        st.session_state["recommendations"] = {"error": "Could not generate recommendations"}
                                
                                # Store full analysis in session state
                                st.session_state["analyzed_data"] = {
                                    "extracted_json": extracted_json,
                                    "medical_analysis": medical_analysis,
                                    "heart_risk": heart_risk,
                                    "recommendations": st.session_state["recommendations"]
                                }
                                
                                st.success("✅ Analysis complete!")
        
        with col2:
            if st.button("💾 Save to Database", use_container_width=True):
                if not st.session_state["analyzed_data"]:
                    st.error("❌ Please analyze the report first.")
                else:
                    with st.spinner("Saving to database..."):
                        user_id = st.session_state.get("patient_id", "unknown")
                        save_result = save_report_to_db(
                            user_id,
                            st.session_state["uploaded_file_name"],
                            st.session_state["analyzed_data"]["extracted_json"],
                            st.session_state["user_context"]
                        )
                        
                        if save_result["status"] == "success":
                            st.success("✅ Report saved to database successfully!")
                        else:
                            st.error(f"❌ Failed to save: {save_result['message']}")
    
    # Display Analysis Results (if available in session state)
    if st.session_state["analyzed_data"]:
        st.markdown("---")
        
        medical_analysis = st.session_state["analyzed_data"]["medical_analysis"]
        heart_risk = st.session_state["analyzed_data"]["heart_risk"]
        
        # Top Metrics Row
        st.markdown("<h2 class='section-header'>📊 Quick Metrics</h2>", unsafe_allow_html=True)
        
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            abnormal_count = len(medical_analysis.get("abnormal_findings", []))
            st.metric("Abnormal Values", abnormal_count, delta=None)
        
        with metric_cols[1]:
            total_params = len(medical_analysis.get("parameters", []))
            st.metric("Total Parameters", total_params, delta=None)
        
        with metric_cols[2]:
            if heart_risk.get("has_data"):
                st.metric("Cholesterol/HDL", heart_risk.get("cholesterol_hdl_ratio", "N/A"))
            else:
                st.metric("Cholesterol/HDL", "N/A")
        
        with metric_cols[3]:
            if heart_risk.get("has_data"):
                risk_level = heart_risk.get("risk_level", "Unknown")
                st.metric("Risk Level", risk_level)
            else:
                st.metric("Risk Level", "N/A")
        
        # Tabs for detailed information
        st.markdown("---")
        st.markdown("<h2 class='section-header'>📋 Detailed Analysis</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Blood Parameters", "❤️ Heart Risk", "💡 Recommendations", "📄 Summary"])
        
        # Tab 1: Blood Parameters
        with tab1:
            if medical_analysis.get("parameters"):
                analysis_df = pd.DataFrame([
                    {
                        "Parameter": p.get("name", ""),
                        "Value": p.get("value", ""),
                        "Unit": p.get("display_unit", ""),
                        "Status": p.get("status", ""),
                        "Reference Range": p.get("display_range", "")
                    }
                    for p in medical_analysis["parameters"]
                ])
                
                st.dataframe(analysis_df, use_container_width=True, hide_index=True)
            
            # Display abnormal values
            if medical_analysis.get("abnormal_findings"):
                st.markdown("<h3 class='section-header'>⚠️ Abnormal Values</h3>", unsafe_allow_html=True)
                
                for finding in medical_analysis["abnormal_findings"]:
                    status_color = "#dc3545" if finding["status"] == "High" else "#ffc107"
                    st.markdown(f"""
                        <div class="risk-card" style="border-left-color: {status_color};">
                            <strong>{finding['parameter']}</strong><br>
                            Status: <span style="color: {status_color}; font-weight: bold;">{finding['status']}</span><br>
                            Value: {finding['normalized_value']} {finding['display_unit']}<br>
                            Reference Range: {finding['reference_range'][0]} - {finding['reference_range'][1]}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Tab 2: Cardiovascular Risk
        with tab2:
            if heart_risk.get("has_data"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Cholesterol", f"{heart_risk['total_cholesterol']} mg/dL")
                with col2:
                    st.metric("HDL Cholesterol", f"{heart_risk['hdl']} mg/dL")
                with col3:
                    st.metric("LDL Cholesterol", f"{heart_risk.get('ldl', 'N/A')} mg/dL")
                
                st.markdown(f"""
                    <div class="risk-card" style="border-left-color: {heart_risk['risk_color']};">
                        <strong>Risk Level: <span style="color: {heart_risk['risk_color']};">{heart_risk['risk_level']}</span></strong><br>
                        Cholesterol/HDL Ratio: {heart_risk['cholesterol_hdl_ratio']}<br>
                        Non-HDL Cholesterol: {heart_risk['non_hdl_cholesterol']} mg/dL<br><br>
                        {heart_risk['recommendation']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ Insufficient lipid data for cardiovascular risk assessment.")
        
        # Tab 3: Recommendations
        with tab3:
            if st.session_state.get("recommendations"):
                recommendations = st.session_state["recommendations"]
                
                if isinstance(recommendations, dict):
                    if recommendations.get("insights"):
                        st.markdown("**🔍 Insight Synthesis:**")
                        st.write(recommendations["insights"])
                        st.markdown("---")
                    
                    if recommendations.get("dietary"):
                        st.markdown("**🍎 Dietary Recommendations:**")
                        st.write(recommendations["dietary"])
                        st.markdown("---")
                    
                    if recommendations.get("next_steps"):
                        st.markdown("**👨‍⚕️ Next Steps:**")
                        st.write(recommendations["next_steps"])
                        st.markdown("---")
                else:
                    st.write(recommendations)
                
                st.warning("⚠️ **Medical Disclaimer:** This is an AI-generated interpretation. Please consult a qualified healthcare professional for proper medical advice.")
            else:
                st.info("ℹ️ Recommendations will appear here after analysis.")
        
        # Tab 4: Clinical Summary
        with tab4:
            if medical_analysis.get("summary"):
                st.markdown("<h3 class='section-header'>📋 Clinical Summary</h3>", unsafe_allow_html=True)
                st.info(medical_analysis["summary"])
            else:
                st.info("ℹ️ No summary available.")
            
            with st.expander("🔧 Debug: Raw Extracted JSON"):
                st.json(st.session_state["analyzed_data"]["extracted_json"])
        
        # Download PDF Report (Twin Red Button)
        st.markdown("---")
        st.markdown("<h2 class='section-header'>📥 Export Report</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_df = pd.DataFrame([
                {
                    "Parameter": p.get("name", ""),
                    "Value": p.get("value", ""),
                    "Unit": p.get("display_unit", ""),
                    "Status": p.get("status", ""),
                    "Reference Range": p.get("display_range", "")
                }
                for p in medical_analysis.get("parameters", [])
            ])
            
            pdf_bytes = generate_pdf_report(
                st.session_state.get("patient_id", "unknown"),
                analysis_df,
                heart_risk,
                medical_analysis.get("summary", ""),
                st.session_state.get("recommendations", "")
            )
            
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"blood_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            # Export as JSON
            json_export = json.dumps(st.session_state["analyzed_data"]["extracted_json"], indent=2)
            st.download_button(
                label="📄 Download JSON Data",
                data=json_export,
                file_name=f"blood_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ============================================================================
# PAGE 3: SETTINGS
# ============================================================================

elif selected_page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ Configuration Settings</h1>", unsafe_allow_html=True)
    
    # API Configuration
    st.markdown("<h3 class='section-header'>🔑 Groq API Configuration</h3>", unsafe_allow_html=True)
    
    groq_api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", os.getenv("GROQ_API_KEY", "")),
        type="password",
        placeholder="Enter your Groq API key (get it from https://console.groq.com/keys)"
    )
    if groq_api_key:
        st.session_state["groq_api_key"] = groq_api_key
    
    st.info("💡 **Tip:** Get your free Groq API key from https://console.groq.com/keys")
    
    st.markdown("---")
    
    # Supabase Configuration
    st.markdown("<h3 class='section-header'>☁️ Supabase Configuration (Optional)</h3>", unsafe_allow_html=True)
    
    supabase_url = st.text_input(
        "Supabase URL",
        value=st.session_state.get("supabase_url", os.getenv("SUPABASE_URL", "")),
        placeholder="https://your-project.supabase.co"
    )
    if supabase_url:
        st.session_state["supabase_url"] = supabase_url
    
    supabase_key = st.text_input(
        "Supabase API Key",
        value=st.session_state.get("supabase_key", os.getenv("SUPABASE_KEY", "")),
        type="password",
        placeholder="Enter your Supabase API key"
    )
    if supabase_key:
        st.session_state["supabase_key"] = supabase_key
    
    # Test Connection
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test Supabase Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                try:
                    if not supabase_url or not supabase_key:
                        st.warning("⚠️ Please enter both Supabase URL and API Key.")
                    else:
                        client = create_client(supabase_url, supabase_key)
                        st.success("✅ Supabase connection successful!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
    
    with col2:
        if st.button("🔄 Clear Session Data", use_container_width=True):
            st.session_state["analyzed_data"] = None
            st.session_state["full_text"] = None
            st.session_state["medical_analysis"] = None
            st.session_state["recommendations"] = None
            st.success("✅ Session data cleared!")
    
    st.markdown("---")
    
    # Information Section
    st.markdown("<h3 class='section-header'>ℹ️ About This Application</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **AI Health Diagnostics Agent** is a production-ready application for analyzing blood test reports.
    
    **Features:**
    - 📄 Universal report support (PDF, Images, JSON)
    - 🤖 AI-powered data extraction using Groq LLM
    - 📊 Medical analysis with 30+ blood parameters
    - ❤️ Cardiovascular risk assessment
    - 💡 Personalized health recommendations
    - 📥 Professional PDF report generation
    - ☁️ Cloud data persistence with Supabase
    
    **Important Disclaimer:**
    ⚠️ This application provides AI-generated interpretations for educational purposes only. 
    It is NOT a substitute for professional medical advice. Always consult a qualified healthcare 
    professional for proper diagnosis and treatment.
    """)
    
    st.markdown("---")
    st.info("💾 Your API keys are stored in your session and not saved permanently. For production use, configure them in the `.env` file.")
