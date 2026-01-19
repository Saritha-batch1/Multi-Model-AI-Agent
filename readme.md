# Multi-Model AI Agent for Automated Health Diagnostics (Internship Submission)

## Executive Summary

This project implements a comprehensive Streamlit-based web application that leverages Groq's advanced AI models, including Llama-3.3-70B for text-based reasoning and Llama-4-Scout for vision processing, to automate the analysis of medical blood reports. The system processes uploaded medical images or PDFs, extracts test data, interprets results, identifies health patterns, and generates personalized recommendations, culminating in a professional PDF report. This solution demonstrates the integration of multiple AI models in a cohesive workflow, emphasizing low-latency inference through Groq's Language Processing Units (LPUs).

## Milestone Completion Report

The following table maps each internship milestone to the corresponding code implementation, demonstrating comprehensive fulfillment of project requirements:

| Milestone | Description | Code Implementation |
|-----------|-------------|-------------------|
| **Milestone 1: Data Ingestion & Interpretation** | Implement data ingestion from medical images/PDFs and validate extracted data | - `modules/extraction.py`: Utilizes Groq's Llama-4-Scout vision model to process uploaded medical images, extracting test names, values, and units through advanced optical character recognition and structured data parsing.<br>- `modules/interpretation.py`: Employs Llama-3.3-70B to validate and standardize extracted data, classifying test results as Normal, High, Low, or Critical with clinical reasoning. |
| **Milestone 2: Pattern Recognition & Context** | Develop pattern recognition algorithms and integrate user context | - `modules/analysis.py`: Leverages Llama-3.3-70B to analyze interpreted results for correlations, risk patterns, and organ health assessment, incorporating user context such as age, gender, and medical history for personalized analysis. |
| **Milestone 3: Synthesis & Recommendations** | Generate actionable health recommendations | - `modules/recommendation.py`: Uses Llama-3.3-70B to synthesize analysis results into personalized health plans, including lifestyle recommendations, dietary advice, and follow-up actions tailored to individual patient profiles. |
| **Milestone 4: Orchestration & Reporting** | Create multi-model orchestration and final reporting | - `app.py`: Serves as the central orchestrator, managing the sequential execution of all modules through a unified Streamlit interface with session state management.<br>- `modules/reporting.py`: Generates comprehensive PDF reports using FPDF, consolidating patient data, test results, analysis findings, and recommendations into a professional, downloadable document. |

## Technical Implementation

### Key Technical Features
- **Groq LPU Integration**: The application harnesses Groq's Language Processing Units for ultra-low latency inference, enabling real-time processing of complex medical data across multiple AI models without compromising performance.
- **Multi-Model Architecture**: Seamlessly integrates vision processing (Llama-4-Scout) with text-based reasoning (Llama-3.3-70B) in a single workflow.
- **Modular Design**: Clean separation of concerns across specialized modules for maintainability and scalability.

### Technology Stack
- **Frontend**: Streamlit (Python-based web framework for interactive applications)
- **Backend**: Python 3.10+
- **AI Models**: Groq API (Llama-4-Scout for vision, Llama-3.3-70B for reasoning)
- **PDF Processing**: PDF2Image with Poppler for image conversion
- **Document Generation**: FPDF for professional PDF report creation
- **Environment Management**: python-dotenv for secure API key handling

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Git
- Poppler utilities for PDF processing

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd health-diagnostics-ai-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Poppler**
   - **Windows**: Download and install Poppler from https://blog.alivate.com.au/poppler-windows/
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt-get install poppler-utils`

5. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Obtain your API key from the Groq console at https://console.groq.com/

## Usage Guide

### Running the Application
1. Ensure all dependencies are installed and the virtual environment is activated.
2. Execute the following command:
   ```bash
   streamlit run app.py
   ```
3. Access the application at the provided local URL (typically http://localhost:8506).

### Using the Application
1. **Patient Profile Setup**: Enter patient details (name, age, gender, medical history) in the sidebar.
2. **Upload Medical Report**: Select and upload a medical report image (PNG, JPG, JPEG formats supported).
3. **Run Diagnostics**: Click the "🚀 Run Full Diagnostics" button to initiate automated analysis.
4. **View Results**: The application will sequentially display:
   - Data extraction results
   - Clinical interpretation with status indicators
   - Pattern analysis and risk assessment
   - Personalized health recommendations
5. **Download Report**: Generate and download a comprehensive PDF report containing all findings.

### Workflow Overview
The "Run Full Diagnostics" button orchestrates a complete pipeline:
- **Extraction** (10-15 seconds): Vision AI processes the image
- **Interpretation** (5-10 seconds): Clinical validation of results
- **Analysis** (10-15 seconds): Pattern recognition and risk assessment
- **Recommendations** (5-10 seconds): Personalized health plan generation
- **PDF Generation**: Instant professional report creation

This implementation demonstrates a production-ready AI-powered health diagnostics system suitable for clinical support applications.

## Sample Reports

- `health_report_lokesh_20260119.pdf`: This is a sample PDF report generated from testing on the `2.png` medical report image.
