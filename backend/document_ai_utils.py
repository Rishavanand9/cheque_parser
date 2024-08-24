import os
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

# Path to your service account key file
SERVICE_ACCOUNT_FILE = '/root/google_service_account.json'

# Document AI processor details
PROCESSOR_NAME = "projects/763261229345/locations/us/processors/f2cc892ef0a7408"

def initialize_document_ai_client():
    try:
        # Check if the service account file exists
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

        # Create credentials using the service account file
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # Initialize the Document AI client with explicit credentials
        client_options = ClientOptions(api_endpoint="https://us-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(
            credentials=credentials,
            client_options=client_options
        )

        logger.info("Successfully initialized Document AI client")
        return client

    except Exception as e:
        logger.error(f"Error initializing Document AI client: {str(e)}")
        raise

# Initialize the Document AI client
document_ai_client = initialize_document_ai_client()