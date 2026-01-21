# models.py

# --- Model 1: Parameter Interpretation ---
# Compares individual values against reference ranges [cite: 53]
def run_parameter_interpretation(data, gender="Male"):
    results = []
    
    # Reference ranges often differ by gender (Context)
    ref_ranges = {
        "hemoglobin": {"min": 13.5 if gender == "Male" else 12.0, "max": 17.5 if gender == "Male" else 15.5, "unit": "g/dL"},
        "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
        "cholesterol_total": {"min": 125, "max": 200, "unit": "mg/dL"},
        "ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
        "hdl": {"min": 40, "max": 60, "unit": "mg/dL"}
    }

    for param, value in data.items():
        if param in ref_ranges:
            ref = ref_ranges[param]
            status = "Normal"
            if value < ref['min']: status = "Low"
            if value > ref['max']: status = "High"
            
            results.append({
                "parameter": param,
                "value": value,
                "range": f"{ref['min']}-{ref['max']}",
                "unit": ref['unit'],
                "status": status
            })
    return results

# --- Model 2: Pattern Recognition & Risk ---
# Calculates risk scores and finds correlations [cite: 55]
def run_risk_assessment(data, user_context):
    risks = []
    risk_score = 0 # Arbitrary score 0-10
    
    # Pattern 1: Metabolic Syndrome indicators
    if data.get('glucose_fasting', 0) > 100 and data.get('hdl', 100) < 40:
        risks.append("Metabolic Pattern Identified: High Glucose + Low HDL")
        risk_score += 3

    # Pattern 2: Atherogenic Index (Lipid Ratio)
    if data.get('hdl'):
        ratio = data.get('cholesterol_total', 0) / data.get('hdl')
        if ratio > 5.0:
            risks.append(f"High Cholesterol/HDL Ratio ({ratio:.1f}). Increased cardiovascular risk.")
            risk_score += 4

    return risks, risk_score

# --- Model 3: Contextual Analysis ---
# Adjusts advice based on age/history [cite: 56]
def run_contextual_analysis(base_risks, user_context):
    refined_advice = []
    age = user_context.get('age', 30)

    for risk in base_risks:
        # Age-based modifier
        if "cardiovascular" in risk.lower() and age > 50:
            refined_advice.append(f"URGENT (Age Factor): {risk} - Please consult a cardiologist.")
        else:
            refined_advice.append(f"{risk} - Monitor diet and exercise.")
            
    if not refined_advice:
        refined_advice.append("No significant patterns detected. Maintain healthy habits.")
        
    return refined_advice