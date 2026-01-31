# app.py
from flask import Flask, render_template, request, jsonify
import os
import backend.utils__santhoshini as utils__santhoshini
import backend.models_santhoshini as models_santhoshini
import database

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_report():
    # 1. Parse Inputs
    if 'report' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['report']
    age = int(request.form.get('age'))
    gender = request.form.get('gender')
    
    # Save file
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)

    # 2. Data Extraction & Validation
    raw_data = utils__santhoshini.mock_ocr_pipeline(path)
    clean_data, errors = utils__santhoshini.validate_and_standardize(raw_data)
    
    if errors:
        return jsonify({"error": "Validation Failed", "details": errors}), 400

    # 3. Model 1 Execution (Interpretation)
    interpretation = models_santhoshini.run_parameter_interpretation(clean_data, gender)

    # 4. Model 2 Execution (Risk Assessment)
    context = {"age": age, "gender": gender}
    raw_risks, risk_score = models_santhoshini.run_risk_assessment(clean_data, context)

    # 5. Model 3 Execution (Contextual Refinement)
    final_recommendations = models_santhoshini.run_contextual_analysis(raw_risks, context)

    # 6. Save to Database (Mock user ID 1 for now)
    database.save_report(1, clean_data, risk_score)

    # 7. Construct Response
    return jsonify({
        "interpretation": interpretation,
        "risks": raw_risks,
        "recommendations": final_recommendations,
        "risk_score": risk_score,
        "disclaimer": "AI is not a doctor. Consult a professional."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)