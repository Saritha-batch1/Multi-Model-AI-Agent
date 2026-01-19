import json
from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()

# Set up Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def interpret_results(raw_data: List[Dict]) -> List[Dict]:
    """
    Validate and interpret medical test results using Groq's Llama-3.3-70b model.

    Args:
        raw_data: List of dictionaries with raw extracted medical test data

    Returns:
        List of processed dictionaries with standardized names, status, and interpretations
    """
    if not raw_data:
        return []

    # Construct the prompt for the AI pathologist
    prompt = f"""
You are an expert Pathologist. You will receive a JSON list of raw medical test results. Your job is to:

1. Standardize the test names (e.g., 'Hb', 'Hgb' -> 'Hemoglobin', 'Glu' -> 'Glucose').
2. Compare the 'value' against the 'reference_range' (if provided) or standard medical ranges.
3. Assign a 'status' flag: 'Normal', 'High', 'Low', or 'Critical'.
4. Provide a short, 1-sentence 'interpretation' for the user.

Input data: {json.dumps(raw_data)}

Output strictly valid JSON array of objects with keys: test_name, value, unit, status, interpretation.
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
            # The model might return a JSON object with a key, or directly an array
            data = json.loads(result_text)
            if isinstance(data, dict) and "results" in data:
                return data["results"]
            elif isinstance(data, list):
                return data
            else:
                print(f"Unexpected response format: {result_text}")
                return raw_data  # fallback
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {result_text}")
            return raw_data  # fallback

    except Exception as e:
        print(f"Error in medical interpretation: {e}")
        return raw_data  # fallback to original data