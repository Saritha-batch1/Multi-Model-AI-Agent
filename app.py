import streamlit as st
from PIL import Image
import os
import pandas as pd
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from modules.extraction import extract_medical_data
from modules.interpretation import interpret_results
from modules.analysis import analyze_patterns
from modules.recommendation import generate_recommendations
from modules.reporting import create_pdf_report


# Load environment variables
load_dotenv()

def _display_recommendations(recommendations: Dict):
    """Display the health recommendations in a formatted way."""
    if not recommendations:
        st.error("Unable to generate recommendations. Please try again.")
        return

    # Executive Summary - prominently displayed
    if "summary_text" in recommendations:
        st.markdown("## 📋 Health Status Summary")
        st.markdown(f"<div style='font-size: 18px; line-height: 1.6; padding: 20px; background-color: #2c3e50; border-radius: 10px; border-left: 5px solid #1e90ff;'>{recommendations['summary_text']}</div>", unsafe_allow_html=True)
    # Actionable Recommendations - as a checklist
    if "recommendations" in recommendations and recommendations["recommendations"]:
        st.markdown("## ✅ Actionable Recommendations")

        for i, rec in enumerate(recommendations["recommendations"], 1):
            st.checkbox(f"**{i}.** {rec}", key=f"rec_{i}")

        # Additional encouragement
        st.success("💪 Take it one step at a time! Small changes lead to big improvements.")

    # Disclaimer - in small gray text
    if "disclaimer" in recommendations:
        st.markdown("---")
        st.caption(f"⚠️ **Medical Disclaimer**: {recommendations['disclaimer']}")

def _display_full_results(user_profile: Dict):
    """Display the complete diagnostics results."""
    # Extraction Results
    st.header("🔍 1. Data Extraction")
    st.write(f"**Extraction Method:** {st.session_state.get('extracted_results', [{}])[0].get('extraction_path', 'Unknown') if st.session_state.get('extracted_results') else 'Unknown'}")

    if st.session_state.get('extracted_results'):
        df = pd.DataFrame(st.session_state.extracted_results)
        st.dataframe(df, width='stretch')

    # Interpretation Results
    st.header("🩺 2. Clinical Interpretation")
    if st.session_state.get('interpreted_results'):
        interpreted = st.session_state.interpreted_results

        # Summary metrics
        total_tests = len(interpreted)
        normal_count = sum(1 for r in interpreted if r.get('status') == 'Normal')
        abnormal_count = total_tests - normal_count

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tests", total_tests)
        with col2:
            st.metric("Normal Results", normal_count, delta=f"{normal_count/total_tests*100:.1f}%" if total_tests > 0 else "0%")
        with col3:
            st.metric("Abnormal Results", abnormal_count, delta=f"-{abnormal_count/total_tests*100:.1f}%" if total_tests > 0 else "0%")

        # Detailed results with color coding
        st.subheader("Test Results Overview")
        cols = st.columns(3)
        for i, test in enumerate(interpreted[:9]):  # Show first 9 tests
            col_idx = i % 3
            with cols[col_idx]:
                status_color = {
                    "Normal": "🟢",
                    "High": "🔴",
                    "Low": "🔵",
                    "Critical": "🟠"
                }.get(test.get("status", "Unknown"), "⚪")

                st.metric(
                    label=f"{status_color} {test.get('test_name', 'Unknown')}",
                    value=f"{test.get('value', 'N/A')} {test.get('unit', '')}",
                    delta=test.get("status", "Unknown")
                )

    # Analysis Results
    st.header("🧩 3. Pattern Analysis & Risk Assessment")
    if st.session_state.get('analysis_result'):
        analysis = st.session_state.analysis_result

        # Clinical Summary
        if "summary" in analysis:
            st.info(f"📋 **Clinical Summary**: {analysis['summary']}")

        # Detected Patterns
        if "patterns" in analysis and analysis["patterns"]:
            st.subheader("Detected Patterns")
            for pattern in analysis["patterns"]:
                severity_emoji = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢"
                }.get(pattern.get("severity", "Medium"), "🟡")

                with st.expander(f"{severity_emoji} {pattern.get('condition', 'Unknown Condition')} (Severity: {pattern.get('severity', 'Unknown')})"):
                    st.write("**Evidence:**")
                    for evidence in pattern.get("evidence", []):
                        st.write(f"• {evidence}")

        # Organ Health
        if "organ_health" in analysis and analysis["organ_health"]:
            st.subheader("Organ Health Assessment")
            organ_cols = st.columns(len(analysis["organ_health"]))

            status_colors = {
                "Stable": "🟢",
                "Risk": "🟡",
                "Concerning": "🔴",
                "Unknown": "⚪"
            }

            for i, (organ, status) in enumerate(analysis["organ_health"].items()):
                with organ_cols[i]:
                    color = status_colors.get(status, "⚪")
                    st.metric(label=f"{color} {organ}", value=status)

    # Recommendations
    st.header("💊 4. Personalized Health Recommendations")
    if st.session_state.get('recommendations'):
        _display_recommendations(st.session_state.recommendations)

    # PDF Download
    st.header("📄 Download Professional Report")
    if (st.session_state.get('extracted_results') and
        st.session_state.get('interpreted_results') and
        st.session_state.get('analysis_result') and
        st.session_state.get('recommendations')):

        try:
            pdf_bytes = create_pdf_report(
                patient_data=user_profile,
                test_results=st.session_state.interpreted_results,
                analysis=st.session_state.analysis_result,
                recommendations=st.session_state.recommendations
            )

            st.download_button(
                label="📥 Download Complete Health Report (PDF)",
                data=pdf_bytes,
                file_name=f"health_report_{user_profile.get('name', 'patient').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                width='stretch'
            )
            st.success("💡 Your professional PDF report includes all findings, analysis, and recommendations!")

        except Exception as e:
            st.error(f"Error generating PDF report: {e}")
    else:
        st.warning("Complete all diagnostic steps to generate the PDF report.")

st.title("🩺 AI Health Diagnostics - Complete Medical Analysis")

# Sidebar for patient profile
st.sidebar.header("Patient Profile")

name = st.sidebar.text_input("Full Name", placeholder="Enter patient's full name")
age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
medical_history = st.sidebar.text_area("Medical History / Symptoms", height=100,
                                       placeholder="Enter any relevant medical history, current symptoms, or medications...")

# Create user profile dictionary
user_profile = {
    "name": name,
    "age": age,
    "gender": gender,
    "medical_history": medical_history
}

uploaded_file = st.file_uploader("Upload a medical report image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    if file_type.startswith("image/"):
        image = Image.open(uploaded_file)
        input_data = image
        input_type = "image"
    else:
        st.error("Unsupported file type")
        st.stop()

    # Master "Run Full Diagnostics" button
    if st.button("🚀 Run Full Diagnostics", type="primary", width='stretch'):
        with st.spinner("🔍 Extracting medical data from image..."):
            result = extract_medical_data(input_data, input_type)

        if result.get("results"):
            st.session_state.extracted_results = result["results"]
            st.session_state.extraction_done = True

            with st.spinner("🩺 Analyzing test results..."):
                interpreted_results = interpret_results(result["results"])
            st.session_state.interpreted_results = interpreted_results

            with st.spinner("🧩 Running deep pattern analysis..."):
                analysis_result = analyze_patterns(interpreted_results, user_profile)
            st.session_state.analysis_result = analysis_result

            with st.spinner("💊 Generating personalized health recommendations..."):
                recommendations = generate_recommendations(analysis_result, user_profile)
            st.session_state.recommendations = recommendations

            st.session_state.diagnostics_complete = True
            st.success("✅ Complete diagnostics finished! Scroll down to view results.")
            st.rerun()  # Refresh to show results
        else:
            st.error("No medical data could be extracted from the image.")

    # Display results if diagnostics are complete
    if st.session_state.get('diagnostics_complete', False):
        _display_full_results(user_profile)

else:
    # Welcome message when no file is uploaded
    st.info("👆 Please upload a medical report image to begin AI-powered health diagnostics.")
    st.markdown("""
    ### How it works:
    1. **Upload** a medical report image (lab results, blood work, etc.)
    2. **AI Extraction** - Advanced vision models identify test names and values
    3. **Clinical Analysis** - Medical AI interprets results and flags abnormalities
    4. **Pattern Recognition** - Identifies correlations and health risks
    5. **Personalized Recommendations** - Generates actionable health advice
    6. **Professional Report** - Download comprehensive PDF report
    """)