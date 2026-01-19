import json
from groq import Groq
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Set up Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_recommendations(analysis_results: Dict, user_profile: Dict[str, Any]) -> Dict:
    """
    Generate personalized health recommendations using Groq's Llama-3.3-70b model.

    Args:
        analysis_results: Dictionary containing summary, patterns, and organ health from analysis
        user_profile: Dictionary with patient information (age, gender, medical_history)

    Returns:
        Dictionary containing summary text, recommendations, and disclaimer
    """
    if not analysis_results:
        return {
            "summary_text": "No analysis data available for recommendations.",
            "recommendations": ["Please consult with a healthcare professional for personalized advice."],
            "disclaimer": "This is not medical advice. Please consult a qualified healthcare provider."
        }

    # Extract key information for the prompt
    patterns = analysis_results.get("patterns", [])
    organ_health = analysis_results.get("organ_health", {})
    clinical_summary = analysis_results.get("summary", "")

    # Check for high/medium severity patterns
    high_severity = [p for p in patterns if p.get("severity") == "High"]
    medium_severity = [p for p in patterns if p.get("severity") == "Medium"]

    # Construct the prompt for the AI health coach
    prompt = f"""
You are an empathetic Health Coach. Based on the patient's analysis, generate a personalized health plan.

Patient Profile:
- Age: {user_profile.get('age', 'Unknown')}
- Gender: {user_profile.get('gender', 'Unknown')}
- Medical History/Symptoms: {user_profile.get('medical_history', 'None provided')}

Clinical Analysis Summary: {clinical_summary}

Detected Patterns: {json.dumps(patterns)}

Organ Health Status: {json.dumps(organ_health)}

High Priority Issues: {len(high_severity)} high severity patterns
Medium Priority Issues: {len(medium_severity)} medium severity patterns

Executive Summary: Write a 2-3 sentence overview of their health status in plain English.

Actionable Recommendations: Provide 3-5 specific lifestyle, diet, or follow-up actions based on the patterns and risks identified. Make them practical and achievable.

Formatting: Use clear, encouraging language. Focus on positive, actionable steps.

Disclaimer: Always end with a clear medical disclaimer.

Output strict JSON with this exact structure:
{{
  "summary_text": "2-3 sentence executive summary in plain English",
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3",
    "Specific actionable recommendation 4",
    "Specific actionable recommendation 5"
  ],
  "disclaimer": "Standard medical disclaimer text"
}}

Do not include any other text or explanation.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content.strip()

        # Parse the JSON response
        try:
            data = json.loads(result_text)
            # Validate the structure
            if all(key in data for key in ["summary_text", "recommendations", "disclaimer"]):
                return data
            else:
                print(f"Invalid response structure: {data}")
                return _get_fallback_recommendations()
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {result_text}")
            return _get_fallback_recommendations()

    except Exception as e:
        print(f"Error in recommendation generation: {e}")
        return _get_fallback_recommendations()

def _get_fallback_recommendations() -> Dict:
    """Return fallback recommendations when generation fails."""
    return {
        "summary_text": "Your health analysis has been completed. For personalized recommendations, please consult with a healthcare professional.",
        "recommendations": [
            "Schedule a follow-up appointment with your healthcare provider",
            "Maintain a balanced diet and regular exercise routine",
            "Monitor your symptoms and keep a health journal",
            "Stay hydrated and get adequate sleep",
            "Follow up on any abnormal test results with your doctor"
        ],
        "disclaimer": "This analysis is for informational purposes only and does not constitute medical advice. Please consult a qualified healthcare provider for personalized medical recommendations and treatment."
    }