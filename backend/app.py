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

# Import the database functions
from database_utils import insert_parsed_cheque, get_all_parsed_cheques

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_page(page):
    """
    Attempt to extract text from a page object, handling different possible structures.
    """
    if hasattr(page, 'text'):
        return page.text
    elif hasattr(page, 'text_anchor') and hasattr(page.text_anchor, 'content'):
        return page.text_anchor.content
    elif hasattr(page, 'paragraphs'):
        return ' '.join([p.text for p in page.paragraphs if hasattr(p, 'text')])
    else:
        # Log the available attributes of the page object
        logger.debug(f"Available page attributes: {dir(page)}")
        return ""

def process_document_with_documentai(project_id: str, location: str, processor_id: str, file_content: bytes, mime_type: str):
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    name = client.processor_path(project_id, location, processor_id)

    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )

    result = client.process_document(request=request)
    document = result.document

    # Log available fields for debugging
    logger.debug(f"Document fields: {dir(document)}")
    if document.pages:
        logger.debug(f"Page fields: {dir(document.pages[0])}")

    # Process entities at the document level
    entity_dict = {}
    if hasattr(document, 'entities'):
        for entity in document.entities:
            entity_dict[entity.type_.lower()] = entity.mention_text

    pages_data = []

    import pdb;pdb.set_trace();
    for page in document.pages:
        extracted_data = {
            "bank_name": entity_dict.get("bank_name", ""),
            "date": entity_dict.get("date", ""),
            "ifsc_code": entity_dict.get("ifsc_code", ""),
            "amount_in_words": entity_dict.get("amount_in_words", ""),
            "amount_in_digits": entity_dict.get("amount", ""),
            "payer": entity_dict.get("payer", "") or entity_dict.get("payee", ""),
            "account_number": entity_dict.get("account_number", ""),
            "cheque_number": entity_dict.get("cheque_number", ""),
        }

        # Extract page text
        page_text = extract_text_from_page(page)

        # Extract information from page text using regex if not found in entities
        if not extracted_data["bank_name"]:
            bank_match = re.search(r'(?i)([\w\s]+)\s+bank', page_text)
            if bank_match:
                extracted_data["bank_name"] = bank_match.group(1).strip()

        if not extracted_data["date"]:
            date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b', page_text)
            if date_match:
                extracted_data["date"] = date_match.group(1)

        if not extracted_data["ifsc_code"]:
            ifsc_match = re.search(r'IFSC\s*:?\s*([A-Z]{4}[0-9]{7})', page_text, re.IGNORECASE)
            if ifsc_match:
                extracted_data["ifsc_code"] = ifsc_match.group(1)

        if not extracted_data["amount_in_words"]:
            amount_words_match = re.search(r'(?i)(?:rupees|rs\.?)\s+(.*?)\s+(?:only|ONLY)', page_text)
            if amount_words_match:
                extracted_data["amount_in_words"] = amount_words_match.group(1).strip()

        if not extracted_data["amount_in_digits"]:
            amount_digits_match = re.search(r'₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)', page_text)
            if amount_digits_match:
                extracted_data["amount_in_digits"] = amount_digits_match.group(1).replace(',', '')

        if not extracted_data["payer"]:
            payer_match = re.search(r'(?i)pay\s+(.*?)\s+(?:or\s+bearer|OR\s+BEARER)', page_text)
            if payer_match:
                extracted_data["payer"] = payer_match.group(1).strip()

        if not extracted_data["account_number"]:
            account_matches = re.findall(r'\b\d{9,18}\b', page_text)
            if account_matches:
                extracted_data["account_number"] = max(account_matches, key=len)

        if not extracted_data["cheque_number"]:
            cheque_matches = re.findall(r'\b\d{6}\b', page_text)
            if cheque_matches:
                extracted_data["cheque_number"] = cheque_matches[0]

        pages_data.append({
            "page_number": page.page_number if hasattr(page, 'page_number') else 0,
            "extracted_data": extracted_data,
            "full_text": page_text
        })

    return pages_data

def extract_images_from_pdf(pdf_content):
    images = convert_from_bytes(pdf_content)
    image_data = []
    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        image_data.append({
            "page_number": i + 1,
            "image_data": base64.b64encode(img_byte_arr).decode('utf-8')
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
                project_id = "763261229345"
                location = "us"
                processor_id = "f2cc8892ef0a7408"
                
                pages_data = process_document_with_documentai(
                    project_id, location, processor_id, file_content, "application/pdf"
                )
                
                # Extract images from all pages
                image_data = extract_images_from_pdf(file_content)
                
                # Combine page data with image data
                result = []
                for page in pages_data:
                    page_image = next((img for img in image_data if img["page_number"] == page["page_number"]), None)
                    if page_image:
                        page["image_data"] = page_image["image_data"]
                    result.append(page)
                
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