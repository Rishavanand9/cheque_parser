import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import time
# from google.cloud import documentai
# from google.api_core.client_options import ClientOptions
import io
import re
from pdf2image import convert_from_bytes

from transformers import TrOCRProcessor, VisionEncoderDecoderModel, pipeline
import torch
from PIL import Image
import pytesseract
from fuzzywuzzy import fuzz
import numpy as np
from prompt import EXTRACTION_PROMPT

# Import the database functions
from database_utils import insert_parsed_cheque, get_all_parsed_cheques

app = Flask(__name__)
CORS(app)


# Load Hugging Face model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-printed")
nlp = pipeline("text2text-generation", model="google/flan-t5-base")

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_with_trocr(image):
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def extract_text_with_tesseract(image):
    return pytesseract.image_to_string(image)

def prompt_guided_extraction(combined_text):
    prompt = EXTRACTION_PROMPT.format(extracted_text=combined_text)
    response = nlp(prompt, max_length=1000, num_return_sequences=1)[0]['generated_text']
    
    # Parse the response
    fields = ["Bank Name", "IFSC Code", "Cheque Amount", "Date", "Account Number", "Cheque Number"]
    extracted_data = {}
    
    for field in fields:
        # Use raw string for the regular expression
        match = re.search(r"{}: (.*?) \(Confidence: (\d+)%\)".format(re.escape(field)), response)
        if match:
            value, confidence = match.groups()
            extracted_data[field.lower().replace(" ", "_")] = {
                "value": value.strip(),
                "confidence": float(confidence) / 100,
                "needs_review": float(confidence) < 70 or value.strip() in ["Not Available", "Requires Manual Verification"]
            }
        else:
            extracted_data[field.lower().replace(" ", "_")] = {
                "value": "Not Available",
                "confidence": 0,
                "needs_review": True
            }
    
    return extracted_data

def process_image(image):
    trocr_text = extract_text_with_trocr(image)
    tesseract_text = extract_text_with_tesseract(image)
    
    combined_text = f"TrOCR output:\n{trocr_text}\n\nTesseract output:\n{tesseract_text}"
    
    return prompt_guided_extraction(combined_text)

def extract_images_from_pdf(pdf_content):
    images = convert_from_bytes(pdf_content)
    image_data = []
    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        image_data.append({
            "page_number": i + 1,
            "image_data": base64.b64encode(img_byte_arr).decode('utf-8'),
            "pil_image": image
        })
    return image_data

@app.route('/api/parse-cheque', methods=['POST'])
def upload_file():
    logger.info("Received request to /api/parse-cheque")
    
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            file_content = file.read()
            
            try:
                # Extract images from PDF
                image_data = extract_images_from_pdf(file_content)
                
                # Process each image
                result = []
                for page in image_data:
                    extracted_data = process_image(page['pil_image'])
                    result.append({
                        "page_number": page["page_number"],
                        "image_data": page["image_data"],
                        "extracted_data": extracted_data
                    })
                
                logger.info("Processed PDF successfully")
                return jsonify({"status": "success", "data": result})
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                return jsonify({"status": "error", "message": f"Error processing PDF: {str(e)}"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid file type. Please upload a PDF."}), 400
    except Exception as e:
        logger.error(f"Unexpected error in upload_file: {str(e)}")
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/save-to-db', methods=['POST'])
def save_to_db():
    try:
        data = request.json
        for item in data:
            insert_parsed_cheque(item['extracted_data'])
        return jsonify({"status": "success", "message": "Data saved to database"})
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)