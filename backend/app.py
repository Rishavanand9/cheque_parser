import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from google.cloud import vision
import io
import json
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/google-credentials.json'

# Configure PostgreSQL database
DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class ChequeData(Base):
    __tablename__ = 'cheque_data'

    id = Column(Integer, primary_key=True)
    data = Column(JSON)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def process_image_with_vision_api(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    # Process the response and extract relevant information
    # This is a simplified example; you may need to adjust based on your specific cheque layout
    extracted_data = {
        id: "",
        bank_name: "",
        date: "",
        ifsc_code: "",
        amount_in_words: "",
        amount_in_digits: "",
        payer: "",
        account_number: "",
        cheque_number: "",
        image: "",
        created_at: "",
        updated_at: ""
    }

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join([symbol.text for symbol in word.symbols])
                    # Add logic to identify and extract specific fields based on their position or context
                    # This is a placeholder and should be customized based on your cheque layout
                    if 'DATE' in word_text:
                        extracted_data['date'] = word_text.replace('DATE', '').strip()
                    elif 'PAY' in word_text:
                        extracted_data['payee'] = word_text.replace('PAY', '').strip()
                    # Add more conditions for other fields

    return extracted_data

@app.route('/api/parse-cheque', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Convert PDF to images
        images = convert_from_path(file_path)
        
        results = []
        for i, image in enumerate(images):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'page_{i}.jpg')
            image.save(image_path, 'JPEG')
            
            # Process image with Google Vision API
            extracted_data = process_image_with_vision_api(image_path)
            results.append(extracted_data)
            
            # Clean up temporary image file
            os.remove(image_path)
        
        # Clean up uploaded PDF file
        os.remove(file_path)
        
        return jsonify(results)
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

@app.route('/api/save-data', methods=['POST'])
def save_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    session = Session()
    new_cheque_data = ChequeData(data=data)
    session.add(new_cheque_data)
    session.commit()
    session.close()
    
    return jsonify({"message": "Data saved successfully"}), 200

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Cheque Data', index=False)
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='cheque_data.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True)