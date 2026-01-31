from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import time
import re
import PyPDF2

# Import our custom engines
from synthesis_engine import FindingsSynthesizer
from recommendation_engine import RecommendationGenerator

app = Flask(__name__)
app.secret_key = 'health-ai-secret-2024'

# Initialize engines
synthesizer = FindingsSynthesizer()
recommendation_generator = RecommendationGenerator()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_values_from_pdf(pdf_path):
    """Extract blood parameters from PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            extracted_data = {}
            
            # Common patterns for blood parameters
            patterns = {
                'Hemoglobin': [r'Hemoglobin[\s:]*([\d.]+)', r'Hb[\s:]*([\d.]+)'],
                'WBC Count': [r'WBC[\s:]*([\d.,]+)', r'White[\s\w]*Count[\s:]*([\d.,]+)'],
                'Platelet Count': [r'Platelet[\s:]*([\d.,]+)', r'PLT[\s:]*([\d.,]+)'],
                'RBC': [r'RBC[\s:]*([\d.]+)', r'Red[\s\w]*Cell[\s:]*([\d.]+)'],
                'Glucose': [r'Glucose[\s:]*([\d.]+)', r'Blood[\s\w]*Sugar[\s:]*([\d.]+)'],
                'Cholesterol': [r'Cholesterol[\s:]*([\d.]+)', r'Total[\s\w]*Chol[\s:]*([\d.]+)'],
                'HDL': [r'HDL[\s:]*([\d.]+)'],
                'LDL': [r'LDL[\s:]*([\d.]+)'],
                'Triglycerides': [r'Triglycerides[\s:]*([\d.]+)', r'TG[\s:]*([\d.]+)']
            }
            
            for param_name, param_patterns in patterns.items():
                value_found = None
                for pattern in param_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            value_str = match.group(1).replace(',', '')
                            value_found = float(value_str)
                            break
                        except:
                            continue
                
                # Default values if not found
                if value_found is None:
                    defaults = {
                        'Hemoglobin': 14.0,
                        'WBC Count': 7500,
                        'Platelet Count': 250000,
                        'RBC': 4.7,
                        'Glucose': 95,
                        'Cholesterol': 180,
                        'HDL': 50,
                        'LDL': 100,
                        'Triglycerides': 120
                    }
                    value_found = defaults.get(param_name, 0.0)
                
                extracted_data[param_name] = value_found
            
            return extracted_data
            
    except Exception as e:
        print(f"PDF Error: {e}")
        # Return sample data for demo
        return {
            'Hemoglobin': 13.5,
            'WBC Count': 8500,
            'Platelet Count': 250000,
            'RBC': 4.5,
            'Glucose': 95,
            'Cholesterol': 180,
            'HDL': 55,
            'LDL': 100,
            'Triglycerides': 120
        }

def analyze_blood_report(data, age=None, gender=None):
    """Model 1: Parameter Interpretation"""
    results = []
    
    age = int(age) if age and age.isdigit() else 30
    gender = gender or 'male'
    
    # Hemoglobin analysis
    hb = data.get('Hemoglobin', 0)
    if gender == 'female':
        if hb < 12.0:
            results.append("Low Hemoglobin - Possible Anemia")
        elif hb > 15.5:
            results.append("High Hemoglobin level")
        else:
            results.append("Hemoglobin: Normal range")
    else:
        if hb < 13.5:
            results.append("Low Hemoglobin - Possible Anemia")
        elif hb > 17.5:
            results.append("High Hemoglobin level")
        else:
            results.append("Hemoglobin: Normal range")
    
    # WBC analysis
    wbc = data.get('WBC Count', 0)
    if wbc < 4000:
        results.append("Low WBC count (Leukopenia risk)")
    elif wbc > 11000:
        results.append("High WBC count (Possible Infection)")
    else:
        results.append("WBC Count: Normal range")
    
    # Platelet analysis
    platelets = data.get('Platelet Count', 0)
    if platelets < 150000:
        results.append("Low Platelet count (Thrombocytopenia)")
    elif platelets > 450000:
        results.append("High Platelet count (Thrombocytosis)")
    else:
        results.append("Platelet count: Normal range")
    
    # Glucose analysis
    glucose = data.get('Glucose', 0)
    if glucose < 70:
        results.append("Low Blood Glucose (Hypoglycemia risk)")
    elif glucose > 100:
        if glucose > 126:
            results.append("High Blood Glucose (Possible Diabetes)")
        else:
            results.append("Elevated Blood Glucose (Pre-diabetes range)")
    else:
        results.append("Blood Glucose: Normal range")
    
    # Cholesterol analysis
    cholesterol = data.get('Cholesterol', 0)
    if cholesterol > 200:
        results.append("High Total Cholesterol")
    else:
        results.append("Cholesterol: Normal range")
    
    return results

def analyze_patterns(data, age=None, gender=None):
    """Model 2: Pattern Recognition"""
    patterns = []
    
    # Check metabolic syndrome pattern
    glucose = data.get('Glucose', 0)
    cholesterol = data.get('Cholesterol', 0)
    triglycerides = data.get('Triglycerides', 0)
    
    if glucose > 100 and cholesterol > 200:
        patterns.append("Metabolic syndrome pattern detected")
        if triglycerides > 150:
            patterns.append("High triglycerides increase cardiovascular risk")
    
    # Check anemia pattern
    hb = data.get('Hemoglobin', 0)
    rbc = data.get('RBC', 0)
    if hb < 13 and rbc < 4.5:
        patterns.append("Consistent anemia pattern (low Hb + low RBC)")
    
    # Check infection pattern
    wbc = data.get('WBC Count', 0)
    if wbc > 11000:
        patterns.append("Infection/inflammation pattern detected")
    
    return patterns

def analyze_context(data, age=None, gender=None):
    """Model 3: Contextual Analysis"""
    context_results = []
    
    age_int = int(age) if age and age.isdigit() else 30
    gender_str = gender or 'unspecified'
    
    # Age-based context
    if age_int > 50:
        context_results.append("Age > 50: Increased health monitoring recommended")
        glucose = data.get('Glucose', 0)
        if glucose > 100:
            context_results.append("Age increases diabetes risk - regular screening advised")
    
    if age_int < 18:
        context_results.append("Pediatric values: Use age-specific reference ranges")
    
    # Gender-based context
    if gender_str == 'female':
        hb = data.get('Hemoglobin', 0)
        if hb < 12:
            context_results.append("For women: Consider menstrual cycle in anemia assessment")
    
    if gender_str == 'male':
        cholesterol = data.get('Cholesterol', 0)
        if cholesterol > 200 and age_int > 35:
            context_results.append("For men >35: Regular cholesterol screening advised")
    
    return context_results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    start_time = time.time()
    
    if 'report' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['report']
    
    if file.filename == '':
        return "No file selected", 400
    
    if not allowed_file(file.filename):
        return "Invalid file type", 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get user context
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        
        # Extract data from PDF
        extracted = extract_values_from_pdf(file_path)
        
        # Run all three AI models
        parameter_results = analyze_blood_report(extracted, age, gender)
        pattern_results = analyze_patterns(extracted, age, gender)
        context_results = analyze_context(extracted, age, gender)
        
        # Synthesize findings
        synthesized = synthesizer.synthesize_findings(
            parameter_results,
            pattern_results,
            context_results
        )
        
        # Generate recommendations
        user_context = {
            'age': int(age) if age and age.isdigit() else 30,
            'gender': gender or 'unspecified',
            'medical_history': []
        }
        
        recommendations = recommendation_generator.generate_recommendations(
            synthesized['all_findings'],
            user_context,
            synthesized
        )
        
        processing_time = time.time() - start_time
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Store for template access
        app.config['PARAMETER_RESULTS'] = parameter_results
        app.config['PATTERN_RESULTS'] = pattern_results
        
        return render_template('enhanced_result.html',
                             extracted=extracted,
                             synthesized=synthesized,
                             recommendations=recommendations,
                             filename=filename,
                             timestamp=timestamp,
                             age=age if age else 'Not specified',
                             gender=gender if gender else 'Not specified',
                             processing_time=f"{processing_time:.2f} seconds",
                             parameter_results=parameter_results,
                             pattern_results=pattern_results)
    
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/demo')
def demo():
    """Demo page with sample analysis"""
    # Sample extracted data
    sample_data = {
        'Hemoglobin': 13.5,
        'WBC Count': 8500,
        'Platelet Count': 250000,
        'RBC': 4.5,
        'Glucose': 95,
        'Cholesterol': 180,
        'HDL': 55,
        'LDL': 100,
        'Triglycerides': 120
    }
    
    # Sample AI model results
    parameter_results = [
        "Hemoglobin: Normal range",
        "WBC Count: Normal range",
        "Platelet count: Normal range",
        "Blood Glucose: Normal range",
        "Cholesterol: Normal range"
    ]
    
    pattern_results = [
        "Metabolic indicators within normal limits",
        "No significant pattern abnormalities detected"
    ]
    
    context_results = [
        "General health assessment completed"
    ]
    
    # Synthesize findings
    synthesized = synthesizer.synthesize_findings(
        parameter_results,
        pattern_results,
        context_results
    )
    
    # Generate recommendations
    user_context = {
        'age': 35,
        'gender': 'male',
        'medical_history': []
    }
    
    recommendations = recommendation_generator.generate_recommendations(
        synthesized['all_findings'],
        user_context,
        synthesized
    )
    
    return render_template('enhanced_result.html',
                         extracted=sample_data,
                         synthesized=synthesized,
                         recommendations=recommendations,
                         filename="Sample_Report.pdf",
                         timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                         age="35",
                         gender="Male",
                         processing_time="1.5 seconds",
                         parameter_results=parameter_results,
                         pattern_results=pattern_results)

if __name__ == '__main__':
    print("🚀 AI Health Diagnostics System")
    print("=" * 40)
    print("Starting server on http://localhost:5000")
    print("Demo page: http://localhost:5000/demo")
    print("=" * 40)
    app.run(debug=True, host='0.0.0.0', port=5000)