"""
Week 4: Medical Logic Engine - The Heart
Health Diagnostics AI Agent - Blood Analysis & Risk Assessment

Goal: Process structured data and perform medical analysis.
Focus: Reference ranges, status classification, cardiovascular risk.
"""

import streamlit as st
from PIL import Image
import json
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

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
# REFERENCE RANGES - MEDICAL DATA
# ============================================================================

REFERENCE_RANGES = {
    "glucose": {"name": "Glucose (Fasting)", "unit": "mg/dL", "normal_range": (70, 100)},
    "hemoglobin": {"name": "Hemoglobin", "unit": "g/dL", "normal_range": (12.0, 17.5)},
    "wbc": {"name": "White Blood Cell Count", "unit": "cells/µL", "normal_range": (4000, 11000)},
    "platelets": {"name": "Platelet Count", "unit": "cells/µL", "normal_range": (150000, 450000)},
    "total_cholesterol": {"name": "Total Cholesterol", "unit": "mg/dL", "normal_range": (0, 200)},
    "hdl": {"name": "HDL Cholesterol", "unit": "mg/dL", "normal_range": (40, 300)},
    "ldl": {"name": "LDL Cholesterol", "unit": "mg/dL", "normal_range": (0, 100)},
    "triglycerides": {"name": "Triglycerides", "unit": "mg/dL", "normal_range": (0, 150)},
    "ast": {"name": "AST", "unit": "U/L", "normal_range": (10, 40)},
    "alt": {"name": "ALT", "unit": "U/L", "normal_range": (7, 56)},
    "creatinine": {"name": "Creatinine", "unit": "mg/dL", "normal_range": (0.7, 1.3)},
}

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
    
    .risk-card {
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        margin: 0.5rem 0;
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
# HELPER FUNCTIONS - AI PROCESSING
# ============================================================================

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
    "report_metadata": {"extraction_date": "YYYY-MM-DD", "total_parameters": number},
    "parameters": [{"name": "Parameter Name", "value": numeric_value, "unit": "Unit", "status": "Normal/High/Low"}],
    "summary": "Brief summary of findings"
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

# ============================================================================
# HELPER FUNCTIONS - MEDICAL ANALYSIS
# ============================================================================

def get_parameter_status(value, param_key):
    """Determine if a value is Normal, High, or Low based on reference ranges."""
    if param_key not in REFERENCE_RANGES or value is None:
        return "Unknown"
    
    try:
        value = float(value)
        min_val, max_val = REFERENCE_RANGES[param_key]["normal_range"]
        
        if value < min_val:
            return "Low"
        elif value > max_val:
            return "High"
        else:
            return "Normal"
    except (ValueError, TypeError):
        return "Unknown"


def analyze_blood_data(extracted_json):
    """Analyze blood test data and classify parameters."""
    analysis = {
        "parameters": [],
        "abnormal_findings": [],
        "summary": extracted_json.get("summary", "")
    }
    
    parameters = extracted_json.get("parameters", [])
    
    for param in parameters:
        name = param.get("name", "").lower()
        value = param.get("value")
        unit = param.get("unit", "")
        
        # Find matching reference range
        matched_key = None
        for ref_key in REFERENCE_RANGES.keys():
            if ref_key in name or name in ref_key:
                matched_key = ref_key
                break
        
        if matched_key:
            status = get_parameter_status(value, matched_key)
            ref_range = REFERENCE_RANGES[matched_key]["normal_range"]
            
            analysis["parameters"].append({
                "name": param.get("name", ""),
                "value": value,
                "unit": unit,
                "status": status,
                "reference_range": f"{ref_range[0]} - {ref_range[1]}"
            })
            
            if status in ["High", "Low"]:
                analysis["abnormal_findings"].append({
                    "parameter": param.get("name", ""),
                    "status": status,
                    "value": value,
                    "unit": unit
                })
    
    return analysis


def calculate_heart_risk(analysis_results):
    """Calculate cardiovascular health risk based on lipid panel."""
    heart_risk = {
        "has_data": False,
        "total_cholesterol": None,
        "hdl": None,
        "ldl": None,
        "cholesterol_hdl_ratio": None,
        "risk_level": None,
        "risk_color": None
    }
    
    parameters = analysis_results.get("parameters", [])
    
    for param in parameters:
        name_lower = param.get("name", "").lower()
        value = param.get("value")
        
        if "total cholesterol" in name_lower:
            heart_risk["total_cholesterol"] = value
        elif "hdl" in name_lower:
            heart_risk["hdl"] = value
        elif "ldl" in name_lower:
            heart_risk["ldl"] = value
    
    if heart_risk["total_cholesterol"] and heart_risk["hdl"]:
        try:
            total_chol = float(heart_risk["total_cholesterol"])
            hdl = float(heart_risk["hdl"])
            
            heart_risk["cholesterol_hdl_ratio"] = round(total_chol / hdl, 2)
            
            ratio = heart_risk["cholesterol_hdl_ratio"]
            
            if ratio < 3.5:
                heart_risk["risk_level"] = "Optimal Risk"
                heart_risk["risk_color"] = "#28a745"
            elif ratio <= 5.0:
                heart_risk["risk_level"] = "Moderate Risk"
                heart_risk["risk_color"] = "#ffc107"
            else:
                heart_risk["risk_level"] = "High Risk"
                heart_risk["risk_color"] = "#dc3545"
            
            heart_risk["has_data"] = True
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    
    return heart_risk

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
st.sidebar.markdown("<p style='text-align: center; color: #666666; font-size: 0.9rem;'>v1.3 - Week 4</p>", unsafe_allow_html=True)

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
    - 🤖 AI-powered data extraction
    - 📊 Medical analysis with reference ranges (Week 4 - Active)
    - ❤️ Cardiovascular risk assessment (Week 4 - Active)
    - 💡 Personalized recommendations (coming Week 5)
    - 📥 Download professional reports (coming Week 5)
    """)

# ============================================================================
# PAGE 2: UPLOAD REPORT
# ============================================================================

elif selected_page == "📋 Upload Report":
    st.markdown("<h1 class='main-header'>📋 Blood Report Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood test report and get medical analysis</p>", unsafe_allow_html=True)
    
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
        
        # Display extraction result
        if extraction_result["status"] in ["success", "warning"]:
            if extraction_result["status"] == "success":
                st.success(f"✅ {extraction_result['message']}")
            else:
                st.warning(f"⚠️ {extraction_result['message']}")
            
            # AI Analysis Button
            if st.button("🔍 Analyze with AI", use_container_width=True):
                if not extraction_result.get("text"):
                    st.error("❌ No text to analyze.")
                else:
                    with st.spinner("🤖 AI is analyzing your report..."):
                        groq_api_key = os.getenv("GROQ_API_KEY")
                        
                        if not groq_api_key:
                            st.error("❌ Groq API key not configured.")
                        else:
                            llm_result = parse_report_with_llm(
                                extraction_result.get("text", ""),
                                groq_api_key,
                                user_context
                            )
                            
                            if llm_result["status"] == "error":
                                st.error(f"❌ Analysis Failed: {llm_result['message']}")
                            else:
                                extracted_json = llm_result.get("data", {})
                                
                                # Perform medical analysis
                                medical_analysis = analyze_blood_data(extracted_json)
                                heart_risk = calculate_heart_risk(medical_analysis)
                                
                                # Display Results
                                st.markdown("---")
                                st.markdown("<h2 class='section-header'>📊 Medical Analysis Results</h2>", unsafe_allow_html=True)
                                
                                # Quick Metrics
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Abnormal Values", len(medical_analysis["abnormal_findings"]))
                                with col2:
                                    st.metric("Total Parameters", len(medical_analysis["parameters"]))
                                with col3:
                                    if heart_risk["has_data"]:
                                        st.metric("Cholesterol/HDL", heart_risk["cholesterol_hdl_ratio"])
                                    else:
                                        st.metric("Cholesterol/HDL", "N/A")
                                with col4:
                                    if heart_risk["has_data"]:
                                        st.metric("Risk Level", heart_risk["risk_level"])
                                    else:
                                        st.metric("Risk Level", "N/A")
                                
                                # Blood Parameters Table
                                st.markdown("---")
                                st.markdown("<h3 class='section-header'>📋 Blood Parameters</h3>", unsafe_allow_html=True)
                                
                                if medical_analysis["parameters"]:
                                    df = pd.DataFrame(medical_analysis["parameters"])
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                                
                                # Abnormal Values
                                if medical_analysis["abnormal_findings"]:
                                    st.markdown("---")
                                    st.markdown("<h3 class='section-header'>⚠️ Abnormal Values</h3>", unsafe_allow_html=True)
                                    
                                    for finding in medical_analysis["abnormal_findings"]:
                                        color = "#dc3545" if finding["status"] == "High" else "#ffc107"
                                        st.markdown(f"""
                                            <div class="risk-card" style="border-left-color: {color};">
                                                <strong>{finding['parameter']}</strong><br>
                                                Status: <span style="color: {color}; font-weight: bold;">{finding['status']}</span><br>
                                                Value: {finding['value']} {finding['unit']}
                                            </div>
                                        """, unsafe_allow_html=True)
                                
                                # Heart Risk Assessment
                                if heart_risk["has_data"]:
                                    st.markdown("---")
                                    st.markdown("<h3 class='section-header'>❤️ Cardiovascular Risk Assessment</h3>", unsafe_allow_html=True)
                                    
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
                                            Cholesterol/HDL Ratio: {heart_risk['cholesterol_hdl_ratio']}
                                        </div>
                                    """, unsafe_allow_html=True)
                                
                                # Clinical Summary
                                if medical_analysis["summary"]:
                                    st.markdown("---")
                                    st.markdown("<h3 class='section-header'>📋 Clinical Summary</h3>", unsafe_allow_html=True)
                                    st.info(medical_analysis["summary"])
        else:
            st.error(f"❌ {extraction_result['message']}")

# ============================================================================
# PAGE 3: SETTINGS
# ============================================================================

elif selected_page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ Configuration Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-header'>🔑 Groq API Configuration</h3>", unsafe_allow_html=True)
    
    groq_api_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="Enter your Groq API key"
    )
    
    if groq_api_key:
        st.success("✅ API key configured")
    else:
        st.warning("⚠️ No API key found. Get one from https://console.groq.com/keys")
    
    st.markdown("---")
    st.markdown("<h3 class='section-header'>ℹ️ About This Application</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **AI Health Diagnostics Agent** - Week 4: Medical Logic Engine
    
    **What's Implemented:**
    - ✅ File extraction (PDF, Images, JSON)
    - ✅ Groq LLM integration
    - ✅ Blood parameter analysis
    - ✅ Reference range validation
    - ✅ Cardiovascular risk calculation
    - ✅ Results display in tables and cards
    
    **Development Progress:**
    - ✅ Week 1: UI & Structure
    - ✅ Week 2: Data Ingestion
    - ✅ Week 3: AI Integration
    - ✅ Week 4: Medical Logic (Current)
    - ⏳ Week 5: Persistence & Reporting
    - ⏳ Week 6: Final Polish
    """)
    
    st.info("💡 This is a learning project demonstrating progressive development over 6 weeks.")
