"""
Week 5: Persistence & Reporting - The Utility
Health Diagnostics AI Agent - PDF & Database Integration

Goal: Add PDF report generation and database persistence.
Focus: FPDF2 for PDF, Supabase for database, session state management.
"""

import streamlit as st
from PIL import Image
import json
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(
    page_title="🏥 Health Diagnostics AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


def extract_text_from_pdf(uploaded_file):
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
    try:
        json_data = json.load(uploaded_file)
        json_text = json.dumps(json_data, indent=2)
        return {"status": "success", "message": "JSON loaded successfully", "text": json_text}
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse JSON: {str(e)}"}

def parse_report_with_llm(raw_text, api_key, user_context=""):
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

def get_parameter_status(value, param_key):
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

def generate_pdf_report(user_id, analysis_df, heart_risk_data, summary):
    if not FPDF_AVAILABLE:
        return None
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_fill_color(255, 75, 75)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(0, 12, "Blood Test Analysis Report", ln=True, align="C", fill=True)
        pdf.set_draw_color(255, 75, 75)
        pdf.set_line_width(1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)
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
        pdf.set_fill_color(255, 75, 75)
        pdf.set_text_color(255, 255, 255)
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
            if status == "High" or status == "Low":
                pdf.set_text_color(220, 53, 69)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(40, 6, param_name, border=1)
            pdf.cell(25, 6, value, border=1)
            pdf.cell(25, 6, unit, border=1)
            pdf.cell(30, 6, status, border=1)
            pdf.cell(40, 6, ref_range, border=1, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        pdf.set_font("Arial", "B", size=10)
        pdf.cell(0, 8, "IMPORTANT DISCLAIMER", ln=True)
        pdf.set_font("Arial", size=8)
        disclaimer_text = "This is an AI-generated interpretation based on blood test values. It is NOT a medical diagnosis. Please consult a qualified healthcare professional for proper medical advice, diagnosis, and treatment."
        pdf.multi_cell(0, 4, disclaimer_text)
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Failed to generate PDF: {str(e)}")
        return None

def save_report_to_db(user_id, file_name, extracted_json, user_context):
    if not SUPABASE_AVAILABLE:
        return {"status": "error", "message": "Supabase library is not installed"}
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            return {"status": "error", "message": "Supabase credentials not configured"}
        client = create_client(supabase_url, supabase_key)
        report_data = {
            "user_id": user_id,
            "file_name": file_name,
            "extracted_data": extracted_json,
            "user_context": user_context,
            "created_at": datetime.now().isoformat()
        }
        response = client.table("blood_reports").insert(report_data).execute()
        return {"status": "success", "message": "Report saved to database successfully", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save report: {str(e)}"}

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

st.sidebar.title("🏥 Health Diagnostics")
selected_page = st.sidebar.radio("Navigation", ["🏠 Home", "📋 Upload Report", "⚙️ Settings"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; color: #666666; font-size: 0.9rem;'>v1.4 - Week 5</p>", unsafe_allow_html=True)

if selected_page == "🏠 Home":
    st.title("🏥 AI Health Diagnostics Agent")
    st.markdown("Upload your blood report to get instant insights")
    st.info("👋 Welcome! This application helps you analyze blood test reports using AI.")
    st.markdown("""
    ### Features:
    - 📄 Upload blood test reports (PDF, Images, JSON)
    - 📖 Extract text from documents
    - 🤖 AI-powered data extraction
    - 📊 Medical analysis with reference ranges
    - ❤️ Cardiovascular risk assessment
    - 📥 Download professional PDF reports
    - 💾 Save to cloud database
    """)

elif selected_page == "📋 Upload Report":
    st.title("📋 Blood Report Analysis")
    st.markdown("Upload your blood test report and get analysis")
    uploaded_file = st.file_uploader("Upload your blood report", type=["pdf", "png", "jpg", "jpeg", "json"], help="Supported formats: PDF, PNG, JPG, JPEG, JSON")
    user_context = st.text_area("Tell us about your symptoms or reason for the test", placeholder="E.g., 'Feeling fatigued for 2 weeks'", height=80)
    
    if uploaded_file:
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.session_state["user_context"] = user_context
        if uploaded_file.type == "application/pdf":
            extraction_result = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            extraction_result = extract_text_from_image(image)
        elif uploaded_file.type == "application/json":
            extraction_result = extract_text_from_json(uploaded_file)
        else:
            extraction_result = {"status": "error", "message": "Unsupported file type"}
        
        if extraction_result["status"] in ["success", "warning"]:
            if extraction_result["status"] == "success":
                st.success(f"✅ {extraction_result['message']}")
            else:
                st.warning(f"⚠️ {extraction_result['message']}")
            st.session_state["full_text"] = extraction_result.get("text", "")
            with st.expander("📄 View Raw Extracted Text"):
                st.text_area("Extracted content:", value=st.session_state["full_text"], height=200, disabled=True, label_visibility="collapsed")
        else:
            st.error(f"❌ {extraction_result['message']}")
        
        st.markdown("---")
        if st.button("🔍 Analyze with AI", use_container_width=True):
            if not st.session_state["full_text"]:
                st.error("❌ No text to analyze.")
            else:
                with st.spinner("🤖 AI is analyzing your report..."):
                    groq_api_key = os.getenv("GROQ_API_KEY")
                    if not groq_api_key:
                        st.error("❌ Groq API key not configured.")
                    else:
                        llm_result = parse_report_with_llm(st.session_state["full_text"], groq_api_key, st.session_state["user_context"])
                        if llm_result["status"] == "error":
                            st.error(f"❌ Analysis Failed: {llm_result['message']}")
                        else:
                            extracted_json = llm_result.get("data", {})
                            medical_analysis = analyze_blood_data(extracted_json)
                            st.session_state["medical_analysis"] = medical_analysis
                            heart_risk = calculate_heart_risk(medical_analysis)
                            st.session_state["analyzed_data"] = {
                                "extracted_json": extracted_json,
                                "medical_analysis": medical_analysis,
                                "heart_risk": heart_risk
                            }
                            st.success("✅ Analysis complete!")
        
        if st.session_state["analyzed_data"]:
            st.markdown("---")
            st.subheader("📊 Medical Analysis Results")
            medical_analysis = st.session_state["analyzed_data"]["medical_analysis"]
            heart_risk = st.session_state["analyzed_data"]["heart_risk"]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Abnormal Values", len(medical_analysis.get("abnormal_findings", [])))
            with col2:
                st.metric("Total Parameters", len(medical_analysis.get("parameters", [])))
            with col3:
                if heart_risk.get("has_data"):
                    st.metric("Cholesterol/HDL", heart_risk.get("cholesterol_hdl_ratio", "N/A"))
                else:
                    st.metric("Cholesterol/HDL", "N/A")
            with col4:
                if heart_risk.get("has_data"):
                    st.metric("Risk Level", heart_risk.get("risk_level", "N/A"))
                else:
                    st.metric("Risk Level", "N/A")
            
            st.markdown("---")
            st.subheader("📋 Blood Parameters")
            if medical_analysis.get("parameters"):
                analysis_df = pd.DataFrame([
                    {
                        "Parameter": p.get("name", ""),
                        "Value": p.get("value", ""),
                        "Unit": p.get("unit", ""),
                        "Status": p.get("status", ""),
                        "Reference Range": p.get("reference_range", "")
                    }
                    for p in medical_analysis["parameters"]
                ])
                st.dataframe(analysis_df, use_container_width=True, hide_index=True)
            
            if medical_analysis.get("abnormal_findings"):
                st.markdown("---")
                st.subheader("⚠️ Abnormal Values")
                for finding in medical_analysis["abnormal_findings"]:
                    color = "#dc3545" if finding["status"] == "High" else "#ffc107"
                    st.markdown(f"**{finding['parameter']}** - {finding['status']}: {finding['value']} {finding['unit']}")
            
            if heart_risk.get("has_data"):
                st.markdown("---")
                st.subheader("❤️ Cardiovascular Risk Assessment")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Cholesterol", f"{heart_risk['total_cholesterol']} mg/dL")
                with col2:
                    st.metric("HDL Cholesterol", f"{heart_risk['hdl']} mg/dL")
                with col3:
                    st.metric("LDL Cholesterol", f"{heart_risk.get('ldl', 'N/A')} mg/dL")
                st.markdown(f"**Risk Level:** {heart_risk['risk_level']} (Ratio: {heart_risk['cholesterol_hdl_ratio']})")
            
            if medical_analysis.get("summary"):
                st.markdown("---")
                st.subheader("📋 Clinical Summary")
                st.info(medical_analysis["summary"])
            
            st.markdown("---")
            st.subheader("📥 Export Report")
            col1, col2 = st.columns(2)
            with col1:
                analysis_df = pd.DataFrame([
                    {
                        "Parameter": p.get("name", ""),
                        "Value": p.get("value", ""),
                        "Unit": p.get("unit", ""),
                        "Status": p.get("status", ""),
                        "Reference Range": p.get("reference_range", "")
                    }
                    for p in medical_analysis.get("parameters", [])
                ])
                pdf_bytes = generate_pdf_report(
                    "patient_001",
                    analysis_df,
                    heart_risk,
                    medical_analysis.get("summary", "")
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
                if st.button("💾 Save to Database", use_container_width=True):
                    with st.spinner("Saving to database..."):
                        save_result = save_report_to_db(
                            "patient_001",
                            st.session_state["uploaded_file_name"],
                            st.session_state["analyzed_data"]["extracted_json"],
                            st.session_state["user_context"]
                        )
                        if save_result["status"] == "success":
                            st.success("✅ Report saved to database successfully!")
                        else:
                            st.error(f"❌ Failed to save: {save_result['message']}")

elif selected_page == "⚙️ Settings":
    st.title("⚙️ Configuration Settings")
    st.subheader("🔑 Groq API Configuration")
    groq_api_key = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password", placeholder="Enter your Groq API key")
    if groq_api_key:
        st.success("✅ API key configured")
    else:
        st.warning("⚠️ No API key found. Get one from https://console.groq.com/keys")
    
    st.markdown("---")
    st.subheader("☁️ Supabase Configuration (Optional)")
    supabase_url = st.text_input("Supabase URL", value=os.getenv("SUPABASE_URL", ""), placeholder="https://your-project.supabase.co")
    supabase_key = st.text_input("Supabase API Key", value=os.getenv("SUPABASE_KEY", ""), type="password", placeholder="Enter your Supabase API key")
    
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
    
    st.markdown("---")
    st.subheader("ℹ️ About This Application")
    st.markdown("""
    **AI Health Diagnostics Agent** - Week 5: Persistence & Reporting
    
    **What's Implemented:**
    - ✅ File extraction (PDF, Images, JSON)
    - ✅ Groq LLM integration
    - ✅ Blood parameter analysis
    - ✅ Cardiovascular risk calculation
    - ✅ PDF report generation
    - ✅ Supabase database integration
    - ✅ Session state management
    
    **Development Progress:**
    - ✅ Week 1: UI & Structure
    - ✅ Week 2: Data Ingestion
    - ✅ Week 3: AI Integration
    - ✅ Week 4: Medical Logic
    - ✅ Week 5: Persistence & Reporting (Current)
    - ⏳ Week 6: Final Polish
    """)
