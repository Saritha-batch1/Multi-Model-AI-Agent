import json
from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Set up Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_patterns(interpreted_data: List[Dict], user_profile: Dict[str, Any]) -> Dict:
    """
    Perform pattern recognition and context-aware medical analysis using Groq's Llama-3.3-70b model.

    Args:
        interpreted_data: List of interpreted medical test results
        user_profile: Dictionary with patient information (age, gender, medical_history)

    Returns:
        Dictionary containing summary, patterns, and organ health assessment
    """
    if not interpreted_data:
        return {
            "summary": "No test data available for analysis.",
            "patterns": [],
            "organ_health": {}
        }

    # Construct the prompt for the AI diagnostician
    prompt = f"""
You are a Senior Medical Diagnostician. Analyze the patient's blood test results in the context of their profile.

Patient Profile:
- Age: {user_profile.get('age', 'Unknown')}
- Gender: {user_profile.get('gender', 'Unknown')}
- Medical History/Symptoms: {user_profile.get('medical_history', 'None provided')}

Test Results: {json.dumps(interpreted_data)}

Identify Patterns: Look for correlations (e.g., 'Low Hemoglobin' + 'Low MCV' -> Suggests Iron Deficiency Anemia).

Risk Assessment: Flag any organ-specific risks (e.g., 'Kidney Function', 'Liver Health', 'Cardiac Risk').

Context Check: Mention if any values are specifically concerning due to the patient's age or gender.

Output strict JSON with this exact structure:
{{
  "summary": "Brief overall assessment considering patient profile",
  "patterns": [
    {{
      "condition": "Medical condition or pattern name",
      "evidence": ["List of test results supporting this"],
      "severity": "High/Medium/Low"
    }}
  ],
  "organ_health": {{
    "Heart": "Stable/Risk/Concerning",
    "Liver": "Stable/Risk/Concerning",
    "Kidney": "Stable/Risk/Concerning",
    "Other": "Any additional organs of concern"
  }}
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
            if all(key in data for key in ["summary", "patterns", "organ_health"]):
                return data
            else:
                print(f"Invalid response structure: {data}")
                return _get_fallback_response()
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {result_text}")
            return _get_fallback_response()

    except Exception as e:
        print(f"Error in pattern analysis: {e}")
        return _get_fallback_response()

def _get_fallback_response() -> Dict:
    """Return a fallback response when analysis fails."""
    return {
        "summary": "Analysis could not be completed. Please consult with a healthcare professional for proper interpretation.",
        "patterns": [],
        "organ_health": {
            "Heart": "Unknown",
            "Liver": "Unknown",
            "Kidney": "Unknown"
        }
    }