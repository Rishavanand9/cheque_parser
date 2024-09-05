import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

def get_database_connection():
    try:
        connection = psycopg2.connect(
            user="admin",
            password="adminis@@33",
            host="172.105.50.148",
            port="5432",
            database="cheque_parser"
        )
        logger.info("Successfully connected to the database")
        return connection
    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        raise

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
        new_party_code = str(uuid.uuid4())

        insert_query = """
        INSERT INTO parsed_cheques_table 
        (bank_name, date, ifsc_code, amount_in_words, amount_in_digits, 
        party_name, account_number, cheque_number, image_path, receiver, party_code, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        record_to_insert = (
            parsed_data.get('bank_name', ''),
            parsed_data.get('date', ''),
            parsed_data.get('ifsc_code', ''),
            parsed_data.get('amount_in_words', ''),
            parsed_data.get('amount_in_digits', ''),
            parsed_data.get('party_name', ''),  # Now using 'party_name'
            parsed_data.get('account_number', ''),
            parsed_data.get('cheque_number', ''),
            parsed_data.get('image_path', ''),
            parsed_data.get('receiver', ''),  # New 'receiver' field
            new_party_code
        )

        cursor.execute(insert_query, record_to_insert)
        connection.commit()
        logger.info("Record inserted successfully into parsed_cheques_table")

        return new_party_code  # Return the new party_code

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
