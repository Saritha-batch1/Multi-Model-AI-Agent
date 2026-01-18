# Week 3: AI Integration - The Brain

## 🎯 Goal
Connect to Groq LLM API and process extracted text into structured JSON data.

## ✅ What's Implemented

### 1. **Groq LLM Integration**
- Uses `llama-3.3-70b-versatile` model
- Fast inference (< 5 seconds)
- Free tier available
- Excellent for medical text analysis

### 2. **`parse_report_with_llm()` Function**
- Sends extracted text to Groq API
- Uses system prompt for medical context
- Requests JSON output
- Handles JSON parsing errors
- Returns structured data

### 3. **AI Analysis Button**
- "Analyze with AI" button in Upload Report page
- Shows spinner during processing
- Displays structured JSON response
- Error handling with debug info

### 4. **JSON Response Structure**
```json
{
    "report_metadata": {
        "extraction_date": "YYYY-MM-DD",
        "total_parameters": number
    },
    "parameters": [
        {
            "name": "Parameter Name",
            "value": numeric_value,
            "unit": "Unit",
            "status": "Normal/High/Low"
        }
    ],
    "summary": "Brief summary of findings"
}
```

### 5. **Error Handling**
- API key validation
- JSON parsing with fallback
- User-friendly error messages
- Debug information for troubleshooting

## 📊 File Structure
```
Week_3_AI_Integration/
├── app.py              # Main application with LLM integration
├── requirements.txt    # Dependencies (added groq, python-dotenv)
├── .env.example       # Template for environment variables
└── README.md          # This file
```

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Add your Groq API key to .env
# GROQ_API_KEY=your_key_here

# Run the app
streamlit run app.py
```

## 💬 What to Tell the Examiner

**"In Week 3, I integrated the Groq LLM API to process extracted blood test text. The application now sends the raw extracted text to the AI model with a carefully crafted system prompt that instructs it to extract blood parameters and return structured JSON. The LLM response is parsed and displayed in the UI, proving that the AI integration works correctly. This demonstrates understanding of API integration, prompt engineering, and JSON handling. The structured data is now ready for medical analysis in Week 4."**

## 🔄 Next Week (Week 4)
- Parse structured JSON data
- Validate against medical reference ranges
- Calculate cardiovascular risk
- Display results in tables and cards

## 📝 Notes
- Groq API is free with rate limits
- Response time is typically 2-5 seconds
- JSON parsing handles code blocks in response
- System prompt is crucial for output quality
- API key should be in .env file (never commit it)

## 🧪 Testing Tips
- Test with a real blood report
- Check JSON parsing with different responses
- Verify error handling with invalid API key
- Monitor API usage on Groq console
- Test with different user contexts

## 🔐 Security Notes
- Never commit .env file
- Use .env.example as template
- Keep API key private
- Use environment variables for secrets
