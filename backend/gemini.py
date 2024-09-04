import base64
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def get_text_from_gemini_api(image_data):
    print("Gemini is processing the image")
    print("*" * 200)

    # Encode the image data to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    prompt = '''
    Analyze the provided cheque image using multiple OCR techniques. Extract the following information and return it in a JSON format:

    {
      "bank_name": "The name of the bank printed on the cheque",
      "ifsc_code": "The 11-character IFSC code of the bank branch",
      "cheque_amount": "The numerical amount for which the cheque is written, formatted with leading zeros to ensure a consistent 6-digit length",
      "date": "The date on which the cheque was issued, formatted as DDMMYYYY (e.g., 01012024 for January 1st, 2024)",
      "account_number": "The account number from which the funds will be drawn",
      "cheque_number": "The unique 6-digit cheque number, typically found at the bottom left or top right of the cheque",
      "transaction_id": "Any transaction ID present in the image, may be named as google transaction id or upi transaction id",
      "message_in_transaction": "Any message, remarks, or description related to the transaction",
      "paid_to": "The name or entity to whom the payment is made",
      "paid_by": "The name or entity making the payment",
      "bank_reference_number": "Any bank reference number present in the image",
      "utr": "Any UTR (Unique Transaction Reference) number present in the image"
    }

    Instructions for Analysis:
    1. Apply multiple OCR methods to improve accuracy and robustness.
    2. Compare results from different OCR methods, prioritizing higher confidence scores.
    3. Use confidence scores to assess the reliability of extracted information.
    4. Pay special attention to handwritten fields (e.g., cheque amount, date).
    5. Cross-reference extracted data against known patterns:
       - Verify IFSC code follows the 11-character format (e.g., ABCD0123456).
       - Ensure date is in correct DDMMYYYY format and represents a valid date.
       - Confirm cheque number consists of exactly 6 digits.
    6. Perform a second pass analysis on handwritten text, dates, and amounts.

    Output Format:
    Return a JSON object with the extracted information. Include a confidence score (0-100) for each field:

    {
      "bank_name": {"value": "extracted_value", "confidence": 95},
      "ifsc_code": {"value": "extracted_value", "confidence": 90},
      "cheque_amount": {"value": "extracted_value", "confidence": 85},
      "date": {"value": "extracted_value", "confidence": 92},
      "account_number": {"value": "extracted_value", "confidence": 88},
      "cheque_number": {"value": "extracted_value", "confidence": 93},
      "transaction_id": {"value": "extracted_value", "confidence": 87},
      "message_in_transaction": {"value": "extracted_value", "confidence": 80},
      "paid_to": {"value": "extracted_value", "confidence": 89},
      "paid_by": {"value": "extracted_value", "confidence": 86},
      "bank_reference_number": {"value": "extracted_value", "confidence": 91},
      "utr": {"value": "extracted_value", "confidence": 84}
    }

    Notes:
    - For fields with low confidence or discrepancies, provide all variant readings in an array and mark them for manual review.
    - If a field cannot be reliably extracted, set its value to null and confidence to 0.
    '''

    try:
        # Configure the API
        genai.configure(api_key=GEMINI_API_KEY)

        # Use gemini-1.5-pro model
        model = genai.GenerativeModel('gemini-1.5-pro')

        print("prompt-----", prompt)
        safe = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        # Generate content
        response = model.generate_content([
            prompt,
            {'mime_type': 'image/jpeg', 'data': base64.b64decode(image_base64)}
        ], 
        safety_settings=safe)

        print("response-----", response)

        # Check if the response has content
        if response.parts:
            extracted_text = response.text
            print(extracted_text)
            return extracted_text
        else:
            error_msg = "No content returned from Gemini API"
            print(error_msg)
            
            # Check for safety ratings
            if hasattr(response, 'prompt_feedback') and hasattr(response.prompt_feedback, 'safety_ratings'):
                safety_ratings = response.prompt_feedback.safety_ratings
                print("Safety ratings:", safety_ratings)
                error_msg += f" Safety ratings: {safety_ratings}"
            else:
                print("No safety ratings available")
                error_msg += " No safety ratings available"
            
            print(error_msg)
            return error_msg

    except Exception as e:
        error_message = f"Error processing image with Gemini API: {str(e)}"
        print(error_message)
        return error_message