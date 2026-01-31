# Week 2: Data Ingestion - The Eyes

## 🎯 Goal
Make the application read files and extract text from multiple formats.

## ✅ What's Implemented

### 1. **File Extraction Functions**

#### `extract_text_from_pdf()`
- Uses `pdfplumber` library
- Extracts text from all pages
- Handles multi-page PDFs
- Returns page count and extracted text

#### `extract_text_from_image()`
- Uses Tesseract OCR
- Supports PNG, JPG, JPEG formats
- Converts image to text
- Handles OCR errors gracefully

#### `extract_text_from_json()`
- Parses JSON files
- Formats JSON for display
- Validates JSON structure

### 2. **File Uploader Widget**
- Accepts: PDF, PNG, JPG, JPEG, JSON
- Displays file name
- Shows extraction status

### 3. **Raw Text Display**
- Shows extracted text in a text area
- Displays character count
- Shows page count for PDFs
- Provides feedback on extraction success

### 4. **Error Handling**
- Graceful error messages
- Library availability checks
- User-friendly warnings

## 📊 File Structure
```
Week_2_Data_Ingestion/
├── app.py              # Main application with extraction functions
├── requirements.txt    # Dependencies (added pdfplumber, pytesseract, PIL)
└── README.md          # This file
```

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract (required for OCR)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Run the app
streamlit run app.py
```

## 💬 What to Tell the Examiner

**"In Week 2, I implemented file extraction capabilities. The application now reads blood test reports in multiple formats - PDF, images, and JSON. I used pdfplumber for PDF extraction and Tesseract OCR for image processing. The extracted text is displayed in the UI, proving that the data ingestion pipeline works correctly. This demonstrates understanding of file I/O, library integration, and error handling. The raw text is now ready to be processed by AI in Week 3."**

## 🔄 Next Week (Week 3)
- Connect to Groq LLM API
- Send extracted text to AI
- Parse JSON response
- Display structured data

## 📝 Notes
- Tesseract must be installed separately
- pdfplumber handles complex PDFs well
- OCR quality depends on image quality
- JSON parsing is straightforward
- All extraction is done client-side (no API calls yet)

## 🧪 Testing Tips
- Test with a real blood report PDF
- Try OCR with a clear image
- Test JSON with structured data
- Check error handling with invalid files
