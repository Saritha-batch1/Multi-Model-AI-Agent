"""
Week 1: UI & Structure - The Skeleton
Health Diagnostics AI Agent - Basic Layout

Goal: Create the visual layout with no logic yet.
Focus: Streamlit page config, sidebar, file uploader, placeholder sections.
"""

import streamlit as st

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
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("<h2 style='text-align: center; color: #333333;'>🏥 Health Diagnostics</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation Menu
selected_page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📋 Upload Report", "⚙️ Settings"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; color: #666666; font-size: 0.9rem;'>v1.0 - Week 1</p>", unsafe_allow_html=True)

# ============================================================================
# PAGE 1: HOME
# ============================================================================

if selected_page == "🏠 Home":
    st.markdown("<h1 class='main-header'>🏥 AI Health Diagnostics Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood report to get instant insights</p>", unsafe_allow_html=True)
    
    st.info("👋 Welcome! This application helps you analyze blood test reports using AI.")
    
    st.markdown("### Features Coming Soon:")
    st.markdown("""
    - 📄 Upload blood test reports (PDF, Images)
    - 🤖 AI-powered data extraction
    - 📊 Medical analysis with 30+ parameters
    - ❤️ Cardiovascular risk assessment
    - 💡 Personalized recommendations
    - 📥 Download professional reports
    """)

# ============================================================================
# PAGE 2: UPLOAD REPORT
# ============================================================================

elif selected_page == "📋 Upload Report":
    st.markdown("<h1 class='main-header'>📋 Blood Report Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your blood test report</p>", unsafe_allow_html=True)
    
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
    
    # Placeholder for results
    if uploaded_file:
        st.markdown("---")
        st.markdown("<h2 class='section-header'>📊 Analysis Results</h2>", unsafe_allow_html=True)
        
        st.info("🔄 Analysis features coming in Week 2...")
        
        # Placeholder sections
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Abnormal Values", "—")
        with col2:
            st.metric("Total Parameters", "—")
        with col3:
            st.metric("Risk Level", "—")
        with col4:
            st.metric("Status", "—")
        
        st.markdown("---")
        st.markdown("<h3 class='section-header'>📋 Detailed Results</h3>", unsafe_allow_html=True)
        st.info("Results will appear here after analysis is implemented...")

# ============================================================================
# PAGE 3: SETTINGS
# ============================================================================

elif selected_page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ Configuration Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 class='section-header'>ℹ️ About This Application</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    **AI Health Diagnostics Agent** is a progressive development project.
    
    **Current Stage:** Week 1 - UI & Structure
    
    **What's Implemented:**
    - ✅ Basic UI layout
    - ✅ Sidebar navigation
    - ✅ File uploader widget
    - ✅ Placeholder sections
    
    **Coming Next:**
    - 📄 File extraction (Week 2)
    - 🤖 AI integration (Week 3)
    - 📊 Medical analysis (Week 4)
    - 💾 Save & export (Week 5)
    - 🎨 Final polish (Week 6)
    """)
    
    st.info("💡 This is a learning project demonstrating progressive development over 6 weeks.")
