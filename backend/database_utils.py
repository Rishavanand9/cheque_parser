import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import random
import string
import os
from psycopg2.extras import execute_values


logger = logging.getLogger(__name__)

def init_db():
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS parsed_cheques_table (
            id SERIAL PRIMARY KEY,
            bank_name TEXT,
            date TEXT,
            ifsc_code TEXT,
            amount_in_words TEXT,
            amount_in_digits TEXT,
            party_name TEXT,
            account_number TEXT,
            cheque_number TEXT,
            image_path TEXT,
            receiver TEXT,
            party_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        logger.info("Database table initialized successfully")
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error initializing database table: {error}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_database_connection():
    try:
        connection = psycopg2.connect(
            user=os.getenv("POSTGRES_USER", "vipul"),
            password=os.getenv("POSTGRES_PASSWORD", "@Support4#"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "cheque_parser")
        )
        logger.info("Successfully connected to the database")
        return connection
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        raise

def generate_party_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def insert_parsed_cheque(parsed_data):
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Check if the account number already exists
        check_account_query = "SELECT party_code FROM parsed_cheques_table WHERE account_number = %s"
        cursor.execute(check_account_query, (parsed_data.get('account_number', ''),))
        existing_party_code = cursor.fetchone()

        if existing_party_code:
            logger.info(f"Account number exists, returning existing party_code: {existing_party_code[0]}")
            return existing_party_code[0]  # Return the existing party_code

        # Generate a unique party_code if account number doesn't exist
        new_party_code = generate_party_code()
        while True:
            cursor.execute("SELECT 1 FROM parsed_cheques_table WHERE party_code = %s", (new_party_code,))
            if not cursor.fetchone():
                break
            new_party_code = generate_party_code()

        # Handle large image_path data
        image_path = parsed_data.get('image_path', '')
        if image_path.startswith('data:image'):
            # Extract base64 data
            _, image_data = image_path.split(',', 1)
            # Convert to bytes
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_path.encode('utf-8')

        insert_query = """
        INSERT INTO parsed_cheques_table 
        (bank_name, date, ifsc_code, amount_in_words, amount_in_digits, 
        party_name, account_number, cheque_number, image_path, receiver, party_code, created_at) 
        VALUES %s
        RETURNING id, length(image_path) as image_path_length
        """
        
        record_to_insert = (
            parsed_data.get('bank_name', ''),
            parsed_data.get('date', ''),
            parsed_data.get('ifsc_code', ''),
            parsed_data.get('amount_in_words', ''),
            parsed_data.get('amount_in_digits', ''),
            parsed_data.get('party_name', ''),
            parsed_data.get('account_number', ''),
            parsed_data.get('cheque_number', ''),
            psycopg2.Binary(image_bytes),  # Use Binary for large data
            parsed_data.get('receiver', ''),
            new_party_code,
            'NOW()'
        )

        # Use execute_values for better performance with large data
        execute_values(cursor, insert_query, [record_to_insert])
        inserted_row = cursor.fetchone()
        connection.commit()

        # Debug: Print inserted row details
        logger.debug(f"Inserted row: id={inserted_row[0]}, image_path_length={inserted_row[1]}")

        logger.info("Record inserted successfully into parsed_cheques_table")

        return new_party_code

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Failed to insert record into parsed_cheques_table: {error}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")

def get_all_parsed_cheques():
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        select_query = "SELECT * FROM parsed_cheques_table ORDER BY created_at DESC"
        cursor.execute(select_query)
        records = cursor.fetchall()

        logger.info(f"Retrieved {len(records)} records from parsed_cheques_table")
        return records

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error retrieving records from parsed_cheques_table: {error}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")

def get_party_code_by_account_number(account_number):
    connection = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        query = "SELECT party_code FROM parsed_cheques_table WHERE account_number = %s"
        cursor.execute(query, (account_number,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error retrieving party_code for account number {account_number}: {error}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("PostgreSQL connection is closed")


init_db()