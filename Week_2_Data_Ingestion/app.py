"""
Week 2: Data Ingestion - The Eyes
Health Diagnostics AI Agent - File Extraction

Goal: Make the app read files and display extracted text.
Focus: PDF extraction, Image OCR, JSON parsing.
"""

import streamlit as st
from PIL import Image
import json

# ============================================================================
# OPTIONAL LIBRARY IMPORTS
# ============================================================================

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🏥 Health Diagnostics AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# BASIC CSS STYLING
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #333333;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        color: #333333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
        border-bottom: 3px solid #FF4B4B;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS - FILE EXTRACTION
# ============================================================================

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using pdfplumber."""
    if not PDF_AVAILABLE:
        return {"status": "error", "message": "pdfplumber not installed"}
    
    try:
        extracted_text = ""
        page_count = 0
        
        with pdfplumber.open(uploaded_file) as pdf:
            page_count = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    extracted_text += f"\n--- Page {page_num} ---\n{page_text}"
        
        if not extracted_text.strip():
            return {"status": "warning", "message": f"PDF loaded but no text found ({page_count} pages)", "text": ""}
        
        return {"status": "success", "message": f"Text extracted from {page_count} page(s)", "text": extracted_text, "page_count": page_count}
    except Exception as e:
        return {"status": "error", "message": f"Failed to extract PDF: {str(e)}"}


def extract_text_from_image(image):
    """Extract text from image using Tesseract OCR."""
    if not OCR_AVAILABLE:
        return {"status": "error", "message": "Tesseract OCR not installed"}
    
    try:
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            return {"status": "warning", "message": "No text detected in image", "text": ""}
        
        return {"status": "success", "message": f"Text extracted ({len(extracted_text)} characters)", "text": extracted_text}
    except Exception as e:
        return {"status": "error", "message": f"OCR extraction failed: {str(e)}"}


def extract_text_from_json(uploaded_file):
    """Extract data from JSON file."""
    try:
        json_data = json.load(uploaded_file)
        json_text = json.dumps(json_data, indent=2)
        return {"status": "success", "message": "JSON loaded successfully", "text": json_text}
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse JSON: {str(e)}"}

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("<h2 style='text-align: center; color: #333333;'>🏥 Health Diagnostics</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

selected_page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📋 Upload Report", "⚙️ Settings"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; color: #666666; font-size: 0.9rem;'>v1.1 - Week 2</p>", unsafe_allow_html=True)

# ============================================================================
# PAGE 1: HOME
# ============================================================================

if selected_page == "🏠 Home":
    st.markdown("<h1 class='main-header'>🏥 AI Health Diagnostics Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood report to get instant insights</p>", unsafe_allow_html=True)
    
    st.info("👋 Welcome! This application helps you analyze blood test reports using AI.")
    
    st.markdown("### Features:")
    st.markdown("""
    - 📄 Upload blood test reports (PDF, Images, JSON)
    - 📖 Extract text from documents
    - 🤖 AI-powered data extraction (coming Week 3)
    - 📊 Medical analysis (coming Week 4)
    - ❤️ Cardiovascular risk assessment (coming Week 4)
    - 💡 Personalized recommendations (coming Week 5)
    - 📥 Download professional reports (coming Week 5)
    """)

# ============================================================================
# PAGE 2: UPLOAD REPORT
# ============================================================================

elif selected_page == "📋 Upload Report":
    st.markdown("<h1 class='main-header'>📋 Blood Report Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood test report and extract text</p>", unsafe_allow_html=True)
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload your blood report",
        type=["pdf", "png", "jpg", "jpeg", "json"],
        help="Supported formats: PDF, PNG, JPG, JPEG, JSON"
    )
    
    # User Context Input
    user_context = st.text_area(
        "Tell us about your symptoms or reason for the test",
        placeholder="E.g., 'Feeling fatigued for 2 weeks', 'Routine checkup'",
        height=80
    )
    
    # File Processing
    if uploaded_file:
        st.markdown("---")
        st.markdown("<h2 class='section-header'>📖 Extracted Text</h2>", unsafe_allow_html=True)
        
        # Determine file type and extract
        if uploaded_file.type == "application/pdf":
            extraction_result = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            extraction_result = extract_text_from_image(image)
        elif uploaded_file.type == "application/json":
            extraction_result = extract_text_from_json(uploaded_file)
        else:
            extraction_result = {"status": "error", "message": "Unsupported file type"}
        
        # Display result
        if extraction_result["status"] == "success":
            st.success(f"✅ {extraction_result['message']}")
            
            # Display extracted text
            st.markdown("### Raw Extracted Text:")
            st.text_area(
                "Extracted content:",
                value=extraction_result.get("text", ""),
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
            
            st.info("💡 This raw text will be sent to the AI in Week 3 for structured analysis.")
        
        elif extraction_result["status"] == "warning":
            st.warning(f"⚠️ {extraction_result['message']}")
        
        else:
            st.error(f"❌ {extraction_result['message']}")
        
        # Placeholder for next steps
        st.markdown("---")
        st.markdown("<h2 class='section-header'>📊 Analysis Results</h2>", unsafe_allow_html=True)
        st.info("🔄 AI analysis coming in Week 3...")

# ============================================================================
# PAGE 3: SETTINGS
# ============================================================================

elif selected_page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ Configuration Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-header'>ℹ️ About This Application</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **AI Health Diagnostics Agent** - Week 2: Data Ingestion
    
    **What's Implemented:**
    - ✅ File uploader (PDF, PNG, JPG, JPEG, JSON)
    - ✅ PDF text extraction (pdfplumber)
    - ✅ Image OCR (Tesseract)
    - ✅ JSON parsing
    - ✅ Raw text display
    
    **Development Progress:**
    - ✅ Week 1: UI & Structure
    - ✅ Week 2: Data Ingestion (Current)
    - ⏳ Week 3: AI Integration
    - ⏳ Week 4: Medical Logic
    - ⏳ Week 5: Persistence & Reporting
    - ⏳ Week 6: Final Polish
    """)
    
    st.markdown("---")
    st.markdown("<h3 class='section-header'>📋 Supported File Formats</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    | Format | Method | Status |
    |--------|--------|--------|
    | PDF | pdfplumber | ✅ Working |
    | PNG | Tesseract OCR | ✅ Working |
    | JPG/JPEG | Tesseract OCR | ✅ Working |
    | JSON | json.load() | ✅ Working |
    """)
    
    st.info("💡 This is a learning project demonstrating progressive development over 6 weeks.")
