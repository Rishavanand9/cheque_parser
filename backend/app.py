import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from pdf2image import convert_from_path
import logging
import time
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
import concurrent.futures
import io
import re


# Import the database functions
from database_utils import insert_parsed_cheque, get_all_parsed_cheques

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_text_from_google_api(image_data):
    logger.info("Document AI is processing the image")
    
    credentials = service_account.Credentials.from_service_account_file('/root/google_service_account.json')
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    name = client.processor_path('document-project-422815', 'us', 'f1b5ccccf850a629')

    document = {"content": image_data, "mime_type": "image/jpeg"}
    
    # Simplified request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=document,
        field_mask="text,entities"
    )
    
    result = client.process_document(request=request)

    extracted_data = {
        "bank_name": "",
        "date": "",
        "ifsc_code": "",
        "amount_in_words": "",
        "amount_in_digits": "",
        "payer": "",
        "account_number": "",
        "cheque_number": "",
    }

    # Process entities
    for entity in result.document.entities:
        if entity.type_ in extracted_data:
            extracted_data[entity.type_] = entity.mention_text

    # If entities didn't provide all information, try to extract from full text
    full_text = result.document.text
    lines = full_text.split('\n')
    
    if not all(extracted_data.values()):
        # Bank name (usually at the top of the cheque)
        if not extracted_data["bank_name"]:
            bank_lines = [line.strip() for line in lines if "BANK" in line.upper()]
            if bank_lines:
                extracted_data["bank_name"] = bank_lines[0]
            else:
                extracted_data["bank_name"] = lines[0].strip() if lines else ""

        # Date
        if not extracted_data["date"]:
            date_match = re.search(r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b', full_text)
            if date_match:
                day, month, year = date_match.groups()
                extracted_data["date"] = f"{day.zfill(2)}/{month.zfill(2)}/{year.zfill(4)}"

        # IFSC code
        if not extracted_data["ifsc_code"]:
            ifsc_match = re.search(r'IFSC\s*:?\s*([A-Z]{4}[0-9]{7})', full_text, re.IGNORECASE)
            if ifsc_match:
                extracted_data["ifsc_code"] = ifsc_match.group(1)

        # Amount in words
        if not extracted_data["amount_in_words"]:
            amount_words_match = re.search(r'(?:Rupees|Rs\.?)\s+(.*?)\s+(?:only|ONLY)', full_text, re.IGNORECASE)
            if amount_words_match:
                extracted_data["amount_in_words"] = amount_words_match.group(1).strip()

        # Amount in digits
        if not extracted_data["amount_in_digits"]:
            amount_digits_match = re.search(r'₹?\s*(\d+(:?\,\d+)*(:?\.\d{2})?)', full_text)
            if amount_digits_match:
                extracted_data["amount_in_digits"] = amount_digits_match.group(1).replace(',', '')

        # Payer name
        if not extracted_data["payer"]:
            pay_match = re.search(r'Pay\s+(.*?)\s+(?:or\s+bearer|OR\s+BEARER)', full_text, re.IGNORECASE)
            if pay_match:
                extracted_data["payer"] = pay_match.group(1).strip()

        # Account number (updated to check for numbers >= 12 digits)
        if not extracted_data["account_number"]:
            account_matches = re.findall(r'\b\d{12,}\b', full_text)
            if account_matches:
                extracted_data["account_number"] = max(account_matches, key=len)

        # Cheque number
        if not extracted_data["cheque_number"]:
            cheque_pattern = r'[⑈⑆](\d{6})[⑈⑆]\s*(\d{9})[⑈⑆]\s*(\d{6})[⑈⑆]\s*(\d{2})'
            cheque_match = re.search(cheque_pattern, full_text)
            if cheque_match:
                extracted_data["cheque_number"] = ''.join(cheque_match.groups())
            else:
                # Fallback: look for any sequence of 6 digits that might represent the cheque number
                digit_sequences = re.findall(r'\b\d{6}\b', full_text)
                if digit_sequences:
                    extracted_data["cheque_number"] = digit_sequences[0]  # Use the first 6-digit sequence

    # Clean up extracted data
    for key, value in extracted_data.items():
        extracted_data[key] = value.strip() if isinstance(value, str) else value

    return extracted_data, '\n'.join(lines)  # Return extracted data and full text separated by new lines
def process_image_with_timeout(image_path, timeout=30):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_image, image_path)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            logger.warning(f"Document AI processing timed out for {image_path}")
            return None

def process_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        extracted_data, full_text = get_text_from_google_api(image_data)
        
        # Encode image to base64 for frontend display
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        return {
            "extracted_data": extracted_data,
            "full_text": full_text,
            "image_data": image_base64,
            "processing_status": "success"
        }
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"error": str(e), "processing_status": "error"}

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
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"Saved uploaded file: {file_path}")
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    images = convert_from_path(file_path)
                    logger.info(f"Converted PDF to {len(images)} images")
                    
                    results = []
                    for i, image in enumerate(images):
                        image_path = os.path.join(temp_dir, f'cheque_{i}.jpg')
                        image.save(image_path, 'JPEG')
                        
                        result = process_image_with_timeout(image_path)
                        if result:
                            results.append(result)
                        else:
                            # If processing failed, include a thumbnail of the image
                            image.thumbnail((100, 100))
                            buffered = io.BytesIO()
                            image.save(buffered, format="JPEG")
                            img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            results.append({
                                "image_data": img_data,
                                "processing_status": "error",
                                "error": "Processing timed out or failed"
                            })
                    
                    logger.info(f"Processed {len(results)} cheque images")

                os.remove(file_path)
                return jsonify({"status": "success", "data": results})
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