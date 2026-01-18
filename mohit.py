"""
Multi-Model AI Agent for Automated Health Diagnostics
Complete Production-Ready Application with Modern Animated UI

Features:
- Universal report ingestion (PDF, Images, JSON)
- AI-powered data extraction using Groq LLM
- Medical analysis engine with 30+ blood parameters
- Cardiovascular risk assessment
- Professional PDF report generation
- Cloud data persistence with Supabase
- Modern gradient backgrounds with glassmorphism
- Animated buttons and smooth transitions
"""

# ============================================================================
# IMPORTS & CONFIGURATION
# ============================================================================

import streamlit as st
import json
import os
import pandas as pd
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
# MODERN ANIMATED CSS STYLING - GLASSMORPHISM DESIGN
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
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Force all sidebar text to WHITE */
    [data-testid="stSidebar"] {
        color: #FFFFFF !important;
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
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #FFFFFF !important;
    }
    
    /* ===== MAIN CONTENT TEXT - DARK GREY FOR READABILITY ===== */
    .stMarkdown, .stMarkdown * {
        color: #333333 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    p, span, label {
        color: #333333 !important;
    }
    
    /* ===== ANIMATED BUTTONS - MODERN GRADIENT ===== */
    .stButton > button {
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        margin: 1rem 0 !important;
    }
    
    /* ===== METRIC CARDS - GLASSMORPHISM ===== */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-left: 4px solid #667eea !important;
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
        color: #667eea !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
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
        color: #1a1a1a !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #999999 !important;
    }
    
    /* ===== FILE UPLOADER - MODERN ===== */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
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
        border-left: 4px solid #667eea !important;
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
        border-bottom: 3px solid #667eea !important;
        padding-bottom: 0.5rem !important;
    }
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
        border-left: 4px solid #ffc107 !important;
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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ===== SMOOTH SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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


def parse_report_with_llm(raw_text, api_key, user_context=""):
    """Process extracted text using Groq LLM to structure blood test data."""
    if not GROQ_AVAILABLE:
        return {"status": "error", "message": "Groq library is not installed"}
    
    if not api_key or api_key.strip() == "":
        return {"status": "error", "message": "Groq API key is required"}
    
    try:
        client = Groq(api_key=api_key)
        
        system_prompt = """You are an expert medical data extraction assistant. Extract all blood test parameters from the provided text.
        
Return ONLY a valid JSON object with this structure:
{
    "report_metadata": {"extraction_date": "YYYY-MM-DD", "total_parameters": number, "user_context": "user's symptom/reason"},
    "parameters": [{"name": "Parameter Name", "value": numeric_value, "unit": "Unit", "reference_range": "min-max", "status": "Normal/High/Low", "clinical_significance": "Brief explanation"}],
    "summary": "Brief summary of findings",
    "context_based_insights": "Specific insights based on user's symptoms"
}"""
        
        context_note = f"\nUser's Context: {user_context}" if user_context else ""
        user_message = f"""Please analyze this blood test report and extract all parameters into structured JSON format:

{raw_text}{context_note}

Remember: Return ONLY valid JSON, no additional text."""
        
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        response_text = message.choices[0].message.content.strip()
        
        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text
            
            structured_data = json.loads(json_str)
            return {"status": "success", "message": "Report analyzed successfully", "data": structured_data}
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Failed to parse LLM response: {str(e)}", "raw_response": response_text}
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
    """Generate a comprehensive PDF report of blood test analysis."""
    if not FPDF_AVAILABLE:
        return None
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(0, 10, "Blood Test Analysis Report", ln=True, align="C")
        
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Patient Information", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"User ID: {user_id}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Clinical Summary", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, summary if summary else "No summary available")
        pdf.ln(3)
        
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
        
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 8, "Blood Parameters", ln=True)
        
        pdf.set_font("Arial", "B", size=9)
        pdf.cell(40, 6, "Parameter", border=1)
        pdf.cell(25, 6, "Value", border=1)
        pdf.cell(25, 6, "Unit", border=1)
        pdf.cell(30, 6, "Status", border=1)
        pdf.cell(40, 6, "Reference Range", border=1, ln=True)
        
        pdf.set_font("Arial", size=8)
        for idx, row in analysis_df.iterrows():
            param_name = str(row.get("Parameter", ""))[:35]
            value = str(row.get("Value", ""))[:20]
            unit = str(row.get("Unit", ""))[:20]
            status = str(row.get("Status", ""))[:25]
            ref_range = str(row.get("Reference Range", ""))[:35]
            
            pdf.cell(40, 6, param_name, border=1)
            pdf.cell(25, 6, value, border=1)
            pdf.cell(25, 6, unit, border=1)
            pdf.cell(30, 6, status, border=1)
            pdf.cell(40, 6, ref_range, border=1, ln=True)
        
        pdf.ln(3)
        
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


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'analyzed_data' not in st.session_state:
    st.session_state['analyzed_data'] = None
if 'full_text' not in st.session_state:
    st.session_state['full_text'] = None
if 'user_context' not in st.session_state:
    st.session_state['user_context'] = ""
if 'uploaded_file_name' not in st.session_state:
    st.session_state['uploaded_file_name'] = None
if 'medical_analysis' not in st.session_state:
    st.session_state['medical_analysis'] = None
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None


# ============================================================================
# SIDEBAR - PATIENT PORTAL
# ============================================================================

with st.sidebar:
    st.markdown("## 🏥 Patient Portal")
    st.markdown("---")
    
    st.markdown("### 📤 Upload Report")
    uploaded_file = st.file_uploader(
        "Choose a blood test report",
        type=['png', 'jpg', 'jpeg', 'pdf', 'json'],
        help="Supported: PNG, JPG, JPEG, PDF, JSON"
    )
    
    st.markdown("### 💬 Your Symptoms")
    user_context = st.text_area(
        "Describe your symptoms or reason for this test",
        placeholder="e.g., 'Feeling tired', 'Routine checkup'",
        height=80,
        help="This helps our AI provide targeted analysis"
    )
    
    st.markdown("### 👤 Patient ID")
    user_id = st.text_input(
        "Your Patient ID (for records)",
        placeholder="e.g., user_123 or your email",
        help="Used to save reports to your profile"
    )
    
    st.markdown("---")
    analyze_button = st.button(
        "🔍 Analyze Report",
        key="analyze_btn",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown("---")
    
    st.markdown("### 🔑 API Configuration")
    
    env_api_key = os.getenv("GROQ_API_KEY", "")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=env_api_key,
        help="Get one at: https://console.groq.com/keys",
        placeholder="gsk_..."
    )
    
    if groq_api_key:
        st.session_state.groq_api_key = groq_api_key
    elif env_api_key:
        st.session_state.groq_api_key = env_api_key
    
    if st.session_state.get("groq_api_key"):
        st.success("✅ Groq API Key loaded")
    else:
        st.warning("⚠️ No Groq API Key found")
    
    st.markdown("---")
    
    st.markdown("### 💾 Database Configuration")
    
    env_supabase_url = os.getenv("SUPABASE_URL", "")
    env_supabase_key = os.getenv("SUPABASE_KEY", "")
    
    supabase_url = st.text_input(
        "Supabase URL",
        value=env_supabase_url,
        help="Your Supabase project URL",
        placeholder="https://your-project.supabase.co"
    )
    
    supabase_key = st.text_input(
        "Supabase API Key",
        type="password",
        value=env_supabase_key,
        help="Your Supabase anon key",
        placeholder="eyJhbGc..."
    )
    
    if supabase_url:
        st.session_state.supabase_url = supabase_url
    elif env_supabase_url:
        st.session_state.supabase_url = env_supabase_url
    
    if supabase_key:
        st.session_state.supabase_key = supabase_key
    elif env_supabase_key:
        st.session_state.supabase_key = env_supabase_key
    
    if st.session_state.get("supabase_url") and st.session_state.get("supabase_key"):
        st.success("✅ Supabase configured")
    else:
        st.info("ℹ️ Supabase is optional")
    
    st.markdown("---")
    st.markdown("### 📊 Version Info")
    st.markdown("**v1.0.0** | Production Ready")


# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

st.markdown('<div class="main-header">🏥 Health Diagnostics AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Blood Report Analysis</div>', unsafe_allow_html=True)

# ============================================================================
# LANDING PAGE (No file uploaded)
# ============================================================================

if uploaded_file is None:
    st.markdown("---")
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-icon">🏥</div>
        <h1>AI Health Diagnostics Agent</h1>
        <div class="hero-subtitle">Upload your blood report to get instant insights powered by AI</div>
        
        <div class="feature-list">
            <div class="feature-item">✅ Upload PDF, Images, or JSON files</div>
            <div class="feature-item">✅ AI-powered data extraction & analysis</div>
            <div class="feature-item">✅ 30+ blood parameters analyzed</div>
            <div class="feature-item">✅ Cardiovascular risk assessment</div>
            <div class="feature-item">✅ Personalized health recommendations</div>
            <div class="feature-item">✅ Professional PDF reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.warning("⚠️ **Medical Disclaimer:** This is an AI tool and NOT a substitute for professional medical advice. Always consult a healthcare professional.")

# ============================================================================
# FILE PROCESSING & ANALYSIS
# ============================================================================

else:
    st.markdown("---")
    
    file_ext = Path(uploaded_file.name).suffix.lower().lstrip('.')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Name", uploaded_file.name[:30])
    with col2:
        st.metric("File Type", file_ext.upper())
    with col3:
        st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
    
    st.markdown("---")
    
    extracted_text = None
    
    if file_ext in ['png', 'jpg', 'jpeg']:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        extraction = extract_text_from_image(image)
        extracted_text = extraction.get("text")
    
    elif file_ext == 'pdf':
        extraction = extract_text_from_pdf(uploaded_file)
        extracted_text = extraction.get("text")
    
    elif file_ext == 'json':
        try:
            extracted_text = json.load(uploaded_file)
        except:
            st.error("Invalid JSON file")
    
    if extracted_text and analyze_button:
        api_key = st.session_state.get("groq_api_key", "")
        
        if not api_key:
            st.error("⚠️ Groq API key is required. Please enter it in the sidebar.")
        else:
            with st.spinner("🔄 Analyzing report with AI..."):
                llm_result = parse_report_with_llm(extracted_text, api_key, user_context)
            
            if llm_result.get("status") == "success":
                st.session_state['analyzed_data'] = llm_result.get("data", {})
                st.session_state['full_text'] = extracted_text
                st.session_state['user_context'] = user_context
                st.session_state['uploaded_file_name'] = uploaded_file.name
                
                medical_analysis = analyze_blood_data(llm_result.get("data", {}))
                st.session_state['medical_analysis'] = medical_analysis
                
                st.success("✅ Analysis complete!")
                st.rerun()
            else:
                st.error(f"❌ {llm_result.get('message')}")
    
    if st.session_state['analyzed_data'] is not None:
        st.markdown("---")
        
        medical_analysis = st.session_state['medical_analysis']
        
        st.markdown('<h3 class="section-header">📊 Key Metrics</h3>', unsafe_allow_html=True)
        
        metric_cols = st.columns(4)
        
        key_params = {}
        for param in medical_analysis["parameters"]:
            name_lower = param["name"].lower()
            if "hemoglobin" in name_lower:
                key_params["Hemoglobin"] = f"{param['normalized_value']} {param['display_unit']}"
            elif "glucose" in name_lower and "random" not in name_lower:
                key_params["Glucose"] = f"{param['normalized_value']} {param['display_unit']}"
            elif "wbc" in name_lower:
                key_params["WBC"] = f"{param['normalized_value']} {param['display_unit']}"
            elif "platelets" in name_lower:
                key_params["Platelets"] = f"{param['normalized_value']} {param['display_unit']}"
        
        for idx, (metric_name, metric_value) in enumerate(list(key_params.items())[:4]):
            with metric_cols[idx]:
                st.metric(metric_name, metric_value)
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["📋 Summary & Insights", "🩸 Detailed Report", "❤️ Heart Health"])
        
        with tab1:
            st.markdown('<h3 class="section-header">📝 Clinical Summary</h3>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="premium-card">
                <p>{medical_analysis.get("summary", "No summary available")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if medical_analysis.get("warnings"):
                st.markdown('<h3 class="section-header">⚠️ Abnormal Values</h3>', unsafe_allow_html=True)
                for warning in medical_analysis["warnings"]:
                    st.warning(warning)
            
            st.markdown('<h3 class="section-header">💡 Personalized Recommendations</h3>', unsafe_allow_html=True)
            
            api_key = st.session_state.get("groq_api_key", "")
            if api_key:
                with st.spinner("🤖 Generating recommendations..."):
                    try:
                        client = Groq(api_key=api_key)
                        
                        abnormal_params = medical_analysis.get("abnormal_findings", [])
                        abnormal_text = "Abnormal Blood Values Found:\n"
                        for finding in abnormal_params:
                            abnormal_text += f"- {finding['parameter']}: {finding['status']}\n"
                        
                        system_prompt = """You are an empathetic medical AI assistant. Analyze the abnormal blood values in context of the user's reported symptoms. 
Provide actionable lifestyle, dietary, and next-step recommendations. Always include a disclaimer."""
                        
                        user_message = f"""User's Symptoms: {user_context if user_context else "Routine checkup"}

{abnormal_text}

Provide personalized recommendations."""
                        
                        message = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            max_tokens=1500,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message}
                            ]
                        )
                        
                        recommendations_text = message.choices[0].message.content.strip()
                        st.markdown(f"""
                        <div class="premium-card">
                            <p>{recommendations_text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Failed to generate recommendations: {str(e)}")
            else:
                st.info("Enter your Groq API key in the sidebar to generate recommendations.")
            
            st.markdown("---")
            st.warning(
                "⚠️ **IMPORTANT DISCLAIMER**: This is an AI-generated interpretation and NOT a medical diagnosis. "
                "Please consult a qualified healthcare professional for proper medical advice."
            )
        
        with tab2:
            st.markdown('<h3 class="section-header">🩸 Blood Parameters Analysis</h3>', unsafe_allow_html=True)
            
            params_data = []
            for param in medical_analysis["parameters"]:
                params_data.append({
                    "Parameter": param["name"],
                    "Value": param["value"],
                    "Unit": param["unit"],
                    "Normalized Value": param["normalized_value"],
                    "Status": param["status"],
                    "Reference Range": param["display_range"],
                    "Category": param["category"]
                })
            
            if params_data:
                df_params = pd.DataFrame(params_data)
                
                def color_status(val):
                    if val == "Normal":
                        return "background-color: #d4edda; color: #155724; font-weight: bold;"
                    elif val == "High":
                        return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
                    elif val == "Low":
                        return "background-color: #fff3cd; color: #856404; font-weight: bold;"
                    else:
                        return "background-color: #e2e3e5; color: #333333;"
                
                styled_df = df_params.style.applymap(color_status, subset=["Status"])
                st.dataframe(styled_df, use_container_width=True)
                
                json_str = json.dumps(st.session_state['analyzed_data'], indent=2)
                st.download_button(
                    label="📥 Download Structured Data (JSON)",
                    data=json_str,
                    file_name="blood_test_structured.json",
                    mime="application/json"
                )
        
        with tab3:
            st.markdown('<h3 class="section-header">❤️ Cardiovascular Health Assessment</h3>', unsafe_allow_html=True)
            
            heart_risk = calculate_heart_risk(medical_analysis)
            
            if heart_risk["has_data"]:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Cholesterol", f"{heart_risk['total_cholesterol']} mg/dL")
                
                with col2:
                    st.metric("HDL Cholesterol", f"{heart_risk['hdl']} mg/dL", delta="(Good)")
                
                with col3:
                    st.metric("LDL Cholesterol", f"{heart_risk['ldl']} mg/dL" if heart_risk['ldl'] else "N/A", delta="(Bad)")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="risk-card" style="border-left-color: {heart_risk['risk_color']};">
                        <strong>Cholesterol/HDL Ratio</strong><br>
                        <span style="font-size: 2rem; color: {heart_risk['risk_color']}; font-weight: bold;">{heart_risk['cholesterol_hdl_ratio']}</span><br>
                        <small>Optimal: < 3.5 | Moderate: 3.5-5.0 | High: > 5.0</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="risk-card" style="border-left-color: {heart_risk['risk_color']};">
                        <strong>Cardiovascular Risk Level</strong><br>
                        <span style="font-size: 1.8rem; color: {heart_risk['risk_color']}; font-weight: bold;">{heart_risk['risk_level']}</span><br>
                        <small>Non-HDL: {heart_risk['non_hdl_cholesterol']} mg/dL</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown('<h4 style="color: #667eea;">💡 Recommendation</h4>', unsafe_allow_html=True)
                
                if heart_risk["risk_level"] == "High Risk":
                    st.error(heart_risk["recommendation"])
                elif heart_risk["risk_level"] == "Moderate Risk":
                    st.warning(heart_risk["recommendation"])
                else:
                    st.success(heart_risk["recommendation"])
            else:
                st.info("ℹ️ Lipid panel data not available for cardiovascular assessment.")
        
        st.markdown("---")
        st.markdown('<h3 class="section-header">💾 Save & Download</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save to Database", use_container_width=True):
                if user_id.strip():
                    with st.spinner("💾 Saving report to database..."):
                        db_result = save_report_to_db(
                            user_id=user_id,
                            file_name=st.session_state['uploaded_file_name'],
                            extracted_json=st.session_state['analyzed_data'],
                            user_context=st.session_state['user_context']
                        )
                    
                    if db_result.get("status") == "success":
                        st.success(db_result.get("message"))
                    else:
                        st.error(db_result.get("message"))
                else:
                    st.warning("⚠️ Please enter a Patient ID to save the report")
        
        with col2:
            params_data = []
            for param in medical_analysis["parameters"]:
                params_data.append({
                    "Parameter": param["name"],
                    "Value": param["value"],
                    "Unit": param["unit"],
                    "Status": param["status"],
                    "Reference Range": param["display_range"]
                })
            
            df_params = pd.DataFrame(params_data) if params_data else pd.DataFrame()
            heart_risk = calculate_heart_risk(medical_analysis)
            
            pdf_bytes = generate_pdf_report(
                user_id=user_id if user_id else "Unknown",
                analysis_df=df_params,
                heart_risk_data=heart_risk,
                summary=medical_analysis.get("summary", ""),
                recommendations=None
            )
            
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"blood_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("ℹ️ FPDF library not installed. Install it using: pip install fpdf2")
