"""
Week 3: AI Integration - The Brain
Health Diagnostics AI Agent - LLM Connection

Goal: Connect to Groq LLM and process extracted text.
Focus: LLM API integration, JSON parsing, structured output.
"""

import streamlit as st
from PIL import Image
import json
import os
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
            # Try to parse JSON
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
st.sidebar.markdown("<p style='text-align: center; color: #666666; font-size: 0.9rem;'>v1.2 - Week 3</p>", unsafe_allow_html=True)

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
    - 🤖 AI-powered data extraction (Week 3 - Active)
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
    st.markdown("<p class='sub-header'>Upload your blood test report and get AI analysis</p>", unsafe_allow_html=True)
    
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
        
        # Display extraction result
        if extraction_result["status"] == "success":
            st.success(f"✅ {extraction_result['message']}")
            
            with st.expander("📄 View Raw Extracted Text"):
                st.text_area(
                    "Extracted content:",
                    value=extraction_result.get("text", ""),
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
        elif extraction_result["status"] == "warning":
            st.warning(f"⚠️ {extraction_result['message']}")
        else:
            st.error(f"❌ {extraction_result['message']}")
        
        # AI Analysis Section
        st.markdown("---")
        st.markdown("<h2 class='section-header'>🤖 AI Analysis</h2>", unsafe_allow_html=True)
        
        if st.button("🔍 Analyze with AI", use_container_width=True):
            if not extraction_result.get("text"):
                st.error("❌ No text to analyze. Please upload a valid file.")
            else:
                with st.spinner("🤖 AI is analyzing your report..."):
                    # Get API key from environment or user input
                    groq_api_key = os.getenv("GROQ_API_KEY")
                    
                    if not groq_api_key:
                        st.error("❌ Groq API key not found. Please configure it in Settings.")
                    else:
                        # Call LLM
                        llm_result = parse_report_with_llm(
                            extraction_result.get("text", ""),
                            groq_api_key,
                            user_context
                        )
                        
                        if llm_result["status"] == "error":
                            st.error(f"❌ Analysis Failed: {llm_result['message']}")
                            if "raw_response" in llm_result:
                                with st.expander("Debug: Raw Response"):
                                    st.text(llm_result["raw_response"][:500])
                        else:
                            st.success("✅ Analysis complete!")
                            
                            # Display structured JSON
                            st.markdown("### 📊 Structured Analysis (JSON):")
                            st.json(llm_result.get("data", {}))
                            
                            st.info("💡 This structured data will be processed further in Week 4 for medical analysis.")

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
    **AI Health Diagnostics Agent** - Week 3: AI Integration
    
    **What's Implemented:**
    - ✅ File extraction (PDF, Images, JSON)
    - ✅ Groq LLM integration
    - ✅ JSON parsing from LLM response
    - ✅ Structured data output
    - ✅ Error handling
    
    **Development Progress:**
    - ✅ Week 1: UI & Structure
    - ✅ Week 2: Data Ingestion
    - ✅ Week 3: AI Integration (Current)
    - ⏳ Week 4: Medical Logic
    - ⏳ Week 5: Persistence & Reporting
    - ⏳ Week 6: Final Polish
    """)
    
    st.markdown("---")
    st.markdown("<h3 class='section-header'>🔗 API Integration</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **Groq LLM Model:** llama-3.3-70b-versatile
    
    **Features:**
    - Fast inference (< 5 seconds)
    - Free tier available
    - Excellent for medical text analysis
    - JSON output support
    
    **How to Get API Key:**
    1. Visit https://console.groq.com/keys
    2. Sign up for free account
    3. Generate API key
    4. Add to `.env` file: `GROQ_API_KEY=your_key_here`
    """)
    
    st.info("💡 This is a learning project demonstrating progressive development over 6 weeks.")
