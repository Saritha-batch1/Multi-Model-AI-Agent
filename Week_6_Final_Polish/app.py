"""
Week 6: Final Polish - The Product
Health Diagnostics AI Agent - Production Ready Application

CRITICAL FIXES:
- max_tokens=8000 for large PDF handling (19+ pages)
- Twin red button styling for consistency
- Red pill sidebar navigation
- Glassmorphism UI design
- Personalized recommendations
- Enhanced error handling

Features:
- Universal report ingestion (PDF, Images, JSON)
- AI-powered data extraction using Groq LLM (8000 tokens)
- Medical analysis engine with 30+ blood parameters
- Cardiovascular risk assessment
- Enhanced PDF report generation with color-coded tables
- Cloud data persistence with Supabase
- Red pill style sidebar navigation
- Twin red button styling
"""

import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import pytesseract
    OCR_AVAILABLE = True
    tesseract_path = os.getenv("TESSERACT_PATH")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
except ImportError:
    OCR_AVAILABLE = False

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

st.set_page_config(
    page_title="🏥 Health Diagnostics AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stApp {
        background: linear-gradient(to right, #ece9e6, #ffffff) !important;
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    .main {
        background: transparent !important;
    }
    
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
    
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E0E0E0 !important;
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
    
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
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
    
    div[role="radiogroup"] label:hover {
        background-color: #F5F5F5 !important;
        transform: translateX(4px) !important;
    }
    
    div[role="radiogroup"] label:has(input:checked) {
        background: #FF4B4B !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    
    div[role="radiogroup"] input[type="radio"] {
        display: none !important;
    }
    
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
    
    [data-testid="stDataFrame"] {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
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
