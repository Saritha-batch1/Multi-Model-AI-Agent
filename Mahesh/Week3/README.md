Week-3 — Pattern Recognition & Basic Risk Scoring
   Milestone-2 — Model-2 Development (Analytical Logic)

1. Overview
Week-3 focuses on building Model-2 (Pattern Recognition & Risk Assessment) on top of the extracted values from Week-1 and Week-2.
Unlike Week-1 (data extraction) and Week-2 (unified file handling), this week is about:
Understanding medical meaning behind extracted numbers
Identifying patterns & abnormalities
Computing basic risk scores for conditions like anemia, diabetes, heart risks
Combining individual parameters into health indicators
This is the first step toward building an AI-driven medical interpretation module.

2. Objectives for Week-3
   
2.1 Build Pattern Recognition Functions
You will implement custom logic to detect patterns such as:
Low Hemoglobin + Low RBC → Anemia Risk
High Glucose + High Cholesterol → Metabolic Syndrome Risk
Low Platelets + Weak CBC → Bleeding Risk
All values normal → Healthy profile

2.2 Generate a Structured Health Insight Output
Your script will produce a JSON / dict containing:
Extracted parameters
Individual parameter classification (Low / Normal / High)
Pattern detection results
Risk category (Low / Moderate / High)
Safe medical explanation (non-diagnostic)
Suggested lifestyle recommendations (optional)
This will later integrate into the final multi-model pipeline.

3. Input Sources for Week-3
Week-3 does NOT extract raw data.
It consumes Week-2 output JSON files.

Example JSON input:
    {
  "hemoglobin": { "value_standard": 12.5, "flag": "low" },
  "rbc_count": { "value_standard": 4.8, "flag": "normal" },
  "platelet_count": { "value_standard": 150000, "flag": "normal" },
  "glucose": { "value_standard": 102, "flag": "high" },
  "cholesterol": { "value_standard": 210, "flag": "high" }
   }
Week-3 algorithm will analyze these.

4. Key Components to Implement
4.1 Individual Parameter Interpretation
Functions to assign risk levels for:
Hemoglobin
RBC
Platelets
Glucose
Cholesterol
Example:
    def evaluate_hemoglobin(value):
        if value < 13:
            return "low"
        if value > 17:
            return "high"
    return "normal"

5. Pattern Recognition Rules
Examples:
if hb_low and rbc_low:
    anemia_risk = "High risk of anemia pattern"

if glucose_high and cholesterol_high:
    metabolic_syndrome = "Strong pattern for metabolic syndrome"

if platelet_low:
    bleeding_risk = "Possible bleeding tendency"

These rules must follow conservative, safe interpretations.

6. Risk Score Calculation
6.1 Cholesterol Ratio Formula

Risk Ratio = Total Cholesterol / HDL
- < 3.5 → Good
- 3.5 to 5.0 → Moderate Risk
- > 5.0 → High Risk

6.2 Glucose Risk Category
< 100 → Normal
100–125 → Prediabetes
≥ 126 → Diabetes Risk

6.3 Anemia Severity
Based on hemoglobin:
| HB Value | Severity |
| -------- | -------- |
| < 8      | Severe   |
| 8–11     | Moderate |
| 11–13    | Mild     |
| > 13     | Normal   |

7. Output Format

Example output JSON:
    {
  "hb_status": "low",
  "glucose_status": "high",
  "cholesterol_status": "high",

  "patterns": [
    "Anemia pattern detected",
    "Metabolic syndrome indicators present"
  ],

  "risk_scores": {
    "cholesterol_ratio": 5.1,
    "cholesterol_risk_level": "high",
    "glucose_risk_level": "prediabetes"
  },

  "overall_health_flag": "moderate-risk",

  "notes": "This is not a medical diagnosis. Please consult a doctor for confirmation."
}


👁️ REAL-TIME FLOW OF THE SYSTEM
Here is the flow in very simple steps:

 Step 1 — User uploads PDF/image/CSV 
This happens in Week-2.

 Step 2 — Week-2 extracts + normalizes
Output saved in:
Week2/output/row_reports/

 Step 3 — You copy these Week-2 JSON files into Week-3
Because Week-3 must analyze them:
Week3/data/week2_json_reports/

 Step 4 — Week-3 script reads each JSON
Inside pattern_recognition_mahesh.py:
Loads hemoglobin, RBC, glucose, etc.
Evaluates ranges
Applies clinical logic
Detects patterns
Calculates risks

 Step 5 — Week-3 generates final analysis
Saved to:
Week3/output/week3_analysis/
Each JSON is similar to:

{
  "hb_status": "low",
  "glucose_status": "high",
  "cholesterol_status": "high",

  "patterns": [
    "Anemia pattern detected",
    "Metabolic syndrome indicators present"
  ],

  "risk_scores": {
    "cholesterol_ratio": 5.1,
    "cholesterol_risk_level": "high",
    "glucose_risk_level": "prediabetes"
  },

  "overall_health_flag": "moderate-risk",

  "notes": "This is not a medical diagnosis. Please consult a doctor."
}

🧠 IS THIS WHAT THE USER WILL SEE?
YES — the Week-3 output is what a user will finally read.

It gives:
parameter classification (low/normal/high)
pattern detection
health risk level
warnings
lifestyle suggestions (optional)


This is the final interpreted result for that document.
