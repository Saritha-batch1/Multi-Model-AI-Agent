# Deployment Guide - Week 6 Final Polish

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended for Learning)

**Easiest deployment option - Free tier available**

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Health Diagnostics AI Agent - Week 6"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repository
   - Choose the branch and app file
   - Click "Deploy"

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to "Settings"
   - Add secrets:
     ```
     GROQ_API_KEY = "your_key_here"
     SUPABASE_URL = "your_url_here"
     SUPABASE_KEY = "your_key_here"
     ```

### Option 2: Heroku (Traditional Deployment)

**Requires Heroku account and CLI**

1. **Create Procfile**
   ```
   web: streamlit run app.py --logger.level=error
   ```

2. **Create runtime.txt**
   ```
   python-3.11.0
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

### Option 3: Docker (Production)

**For containerized deployment**

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD ["streamlit", "run", "app.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t health-diagnostics .
   docker run -p 8501:8501 health-diagnostics
   ```

### Option 4: AWS/Google Cloud (Enterprise)

**For production-grade deployment**

- Use AWS EC2 or Google Cloud Run
- Set up load balancing
- Configure SSL/TLS
- Set up monitoring and logging

## 📋 Pre-Deployment Checklist

- [ ] All dependencies in requirements.txt
- [ ] .env.example created with all variables
- [ ] .gitignore configured properly
- [ ] No hardcoded secrets in code
- [ ] README.md is comprehensive
- [ ] Code is tested locally
- [ ] Error handling is complete
- [ ] Database migrations are ready
- [ ] API keys are valid
- [ ] Tesseract is installed (if using OCR)

## 🔐 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables for secrets**
   ```python
   api_key = os.getenv("GROQ_API_KEY")
   ```

3. **Validate user input**
   ```python
   if not uploaded_file:
       st.error("Please upload a file")
   ```

4. **Use HTTPS only**
   - Streamlit Cloud uses HTTPS by default
   - Configure SSL for custom domains

5. **Limit API access**
   - Use API key restrictions
   - Set rate limits
   - Monitor usage

## 📊 Monitoring & Logging

### Streamlit Cloud
- Built-in logs in dashboard
- Email alerts for errors
- Performance metrics

### Custom Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

## 🔄 Continuous Integration/Deployment

### GitHub Actions Example
```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit Cloud
        run: |
          streamlit run app.py
```

## 📈 Performance Optimization

1. **Cache expensive operations**
   ```python
   @st.cache_data
   def load_data():
       return expensive_operation()
   ```

2. **Optimize images**
   - Compress before upload
   - Use appropriate formats

3. **Database optimization**
   - Add indexes
   - Use connection pooling
   - Optimize queries

4. **API optimization**
   - Batch requests
   - Use caching
   - Implement rate limiting

## 🆘 Troubleshooting

### Common Issues

**Issue**: Tesseract not found
```bash
# Windows
choco install tesseract

# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

**Issue**: API key not working
- Verify key is correct
- Check API quota
- Ensure key has proper permissions

**Issue**: Database connection fails
- Verify credentials
- Check network connectivity
- Ensure database is running

**Issue**: PDF generation fails
- Check FPDF2 installation
- Verify file permissions
- Check disk space

## 📞 Support Resources

- Streamlit Docs: https://docs.streamlit.io
- Groq API Docs: https://console.groq.com/docs
- Supabase Docs: https://supabase.com/docs
- Python Docs: https://docs.python.org

## 🎯 Next Steps

1. Deploy to Streamlit Cloud
2. Share with users
3. Gather feedback
4. Iterate and improve
5. Consider premium features
6. Scale infrastructure as needed

---

**Deployment Status**: Ready for Production

**Recommended**: Start with Streamlit Cloud for simplicity
