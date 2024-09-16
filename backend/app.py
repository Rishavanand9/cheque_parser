import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import time
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
import io
import re
from pdf2image import convert_from_bytes
import json

# Import the database functions
from database_utils import insert_parsed_cheque, get_all_parsed_cheques, get_party_code_by_account_number

# Import the Gemini API function
from gemini import get_text_from_gemini_api

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_images_from_pdf(pdf_content):
    images = convert_from_bytes(pdf_content)
    image_data = []
    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        image_data.append({
            "page_number": i + 1,
            "image_data": img_byte_arr
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
                # Extract images from all pages
                image_data = extract_images_from_pdf(file_content)
                
                result = []
                for page in image_data:
                    gemini_response = get_text_from_gemini_api(page["image_data"])
                    
                    try:
                        json_string = gemini_response.replace("```json", "").replace("```", "").strip()
                        parsed_data = json.loads(json_string)
                        
                        # Fetch or generate party code
                        account_number = parsed_data.get('account_number', {}).get('value', '')
                        party_code = get_party_code_by_account_number(account_number)
                        if not party_code:
                            insert_data = {k: v.get('value', '') if isinstance(v, dict) else v for k, v in parsed_data.items()}
                            party_code = insert_parsed_cheque(insert_data)
                        
                        parsed_data['party_code'] = {'value': party_code, 'confidence': 1.0}
                        
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse Gemini API response as JSON: {gemini_response}")
                        parsed_data = {"error": "Failed to parse response"}
                    
                    result.append({
                        "page_number": page["page_number"],
                        "extracted_data": parsed_data,
                        "image_data": base64.b64encode(page["image_data"]).decode('utf-8')
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
            # Assuming the extracted_data is now a dictionary with 'value' and 'confidence' for each field
            processed_data = {key: value['value'] for key, value in item['extracted_data'].items()}
            insert_parsed_cheque(processed_data)
        return jsonify({"status": "success", "message": "Data saved to database"})
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-all-cheques', methods=['GET'])
def get_all_cheques():
    try:
        cheques = get_all_parsed_cheques()
        if not cheques:
            return jsonify({"status": "success", "data": [], "message": "No cheques found"}), 200
        return jsonify({"status": "success", "data": cheques})
    except Exception as e:
        logger.error(f"Error retrieving cheques from database: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051, debug=True)