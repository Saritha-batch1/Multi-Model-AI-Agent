import base64
from io import BytesIO
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
from groq import Groq
import os
import json
import re
from typing import List, Dict, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_from_image(image: Image.Image) -> Dict:
    """Extract medical test data from image using Vision LLM."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    prompt = """
Extract all medical lab test results visible in this image. Look for test names, values, units, and reference ranges.
Preserve abbreviations (e.g., cGlu, ctHb).
Return ONLY valid JSON in this exact format:

{
  "results": [
    {
      "test_name": "string",
      "value": "string",
      "unit": "string",
      "reference_range": "string"
    }
  ]
}

If no tests are found, return {"results": []}
Do not include any other text or explanation.
"""
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                ]}
            ],
            response_format={"type": "json_object"}
        )
        result_text = response.choices[0].message.content.strip()
        data = json.loads(result_text)
        if "results" not in data or not isinstance(data["results"], list):
            return {"results": []}
        return data
    except Exception as e:
        print(f"Error in vision extraction: {e}")
        return {"results": []}

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def rule_based_pairing(text: str) -> List[Dict[str, str]]:
    """Extract (test_name, value) pairs using regex."""
    pairs = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match pattern: test_name followed by optional separator and numeric value
        match = re.match(r'^(\w[\w\s]*?)\s*[:=]?\s*([+-]?\d+(?:\.\d+)?)$', line)
        if match:
            test_name = match.group(1).strip()
            value = match.group(2).strip()
            pairs.append({"test_name": test_name, "value": value})
    return pairs

def normalize_with_text_llm(pairs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Normalize pairs with Text LLM to add units and ranges."""
    if not pairs:
        return []
    
    prompt = f"""
Normalize these medical test pairs. For each pair, fill in the unit and reference_range if they are standard and obvious from medical knowledge. Leave as empty string if not known. Do not change test_name or value. Do not invent anything.

Input pairs: {json.dumps(pairs)}

Return a JSON array of objects with keys: test_name, value, unit, reference_range
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result_text = response.choices[0].message.content.strip()
        result_text = response.choices[0].message.content.strip()
        data = json.loads(result_text)
        if isinstance(data, list):
            # Direct array response
            for item in data:
                item.setdefault("unit", "")
                item.setdefault("reference_range", "")
            return data
        elif isinstance(data, dict) and "normalized_pairs" in data:
            # Object with normalized_pairs key
            pairs = data["normalized_pairs"]
            for item in pairs:
                item.setdefault("unit", "")
                item.setdefault("reference_range", "")
            return pairs
        else:
            return pairs  # fallback to original
    except Exception as e:
        print(f"Error in text LLM normalization: {e}")
        return pairs

def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Convert PDF pages to images."""
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"PDF file does not exist: {pdf_path}")
            return []

        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            print(f"PDF file is empty: {pdf_path}")
            return []

        print(f"Converting PDF to images: {pdf_path} (size: {file_size} bytes)")

        # Try to read first few bytes to check if it's a valid PDF
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                print(f"File does not appear to be a valid PDF. Header: {header}")
                return []

        # First try to open with pdfplumber to validate the PDF
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"PDF validation successful: {num_pages} pages")
        except Exception as pdf_error:
            print(f"PDF validation failed with pdfplumber: {pdf_error}")
            return []

        # Use the poppler path from environment or default
        poppler_path = os.getenv("POPPLER_PATH", r"C:\poppler-25.12.0\Library\bin")

        # Verify poppler path exists
        if not os.path.exists(poppler_path):
            print(f"Poppler path does not exist: {poppler_path}")
            return []

        # Try standard conversion first
        try:
            images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=150, first_page=1, last_page=1)
            print(f"Successfully converted {len(images)} pages from PDF")
            return images
        except Exception as convert_error:
            print(f"Standard conversion failed: {convert_error}")
            # Try alternative approach with different settings
            try:
                images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=100, first_page=1, last_page=1)
                print(f"Successfully converted {len(images)} pages with alternative settings")
                return images
            except Exception as alt_error:
                print(f"Alternative conversion also failed: {alt_error}")
                raise convert_error  # Re-raise original error

    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        print(f"PDF path: {pdf_path}")
        print(f"Poppler path: {poppler_path}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return []

def extract_from_pdf(pdf_path: str) -> Dict:
    """Extract from PDF with fallback logic."""
    text = extract_text_from_pdf(pdf_path)

    # Check if PDF is likely image-based
    is_image_based = False
    if text:
        # Calculate text density (characters per KB of file size)
        file_size_kb = os.path.getsize(pdf_path) / 1024
        text_density = len(text) / file_size_kb if file_size_kb > 0 else 0

        # Low text density suggests image-based PDF
        if text_density < 10:  # Less than 10 characters per KB
            is_image_based = True
            print(f"Detected image-based PDF (text density: {text_density:.2f} chars/KB)")

    if not text or is_image_based:
        # Fallback to vision for empty text or image-based PDFs
        print("Using vision extraction for PDF (empty text or image-based)")
        images = pdf_to_images(pdf_path)
        if images:
            result = extract_from_image(images[0])
            result["extraction_path"] = "pdf_vision_fallback"
            return result
        else:
            return {"results": [], "extraction_path": "pdf_vision_fallback"}

    pairs = rule_based_pairing(text)
    threshold = 3
    if len(pairs) < threshold:
        # Fallback to vision if too few pairs found
        print(f"Only {len(pairs)} pairs found, falling back to vision")
        images = pdf_to_images(pdf_path)
        if images:
            result = extract_from_image(images[0])
            result["extraction_path"] = "pdf_vision_fallback"
            return result
        else:
            return {"results": [], "extraction_path": "pdf_vision_fallback"}

    # Normalize with text LLM
    normalized = normalize_with_text_llm(pairs)
    return {"results": normalized, "extraction_path": "pdf_text"}

def extract_from_image_input(image: Image.Image) -> Dict:
    """Extract from image input."""
    result = extract_from_image(image)
    result["extraction_path"] = "image"
    return result

def extract_medical_data(input_data: Union[str, Image.Image], input_type: str) -> Dict:
    """Main orchestration function."""
    if input_type == "image":
        return extract_from_image_input(input_data)
    elif input_type == "pdf":
        return extract_from_pdf(input_data)
    else:
        raise ValueError("input_type must be 'image' or 'pdf'")
