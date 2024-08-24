import psycopg2
from psycopg2.extras import RealDictCursor
import logging

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

        insert_query = """
        INSERT INTO parsed_cheques_table 
        (bank_name, date, ifsc_code, amount_in_words, amount_in_digits, 
        payer, account_number, cheque_number, image_path, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        record_to_insert = (
            parsed_data.get('bank_name', ''),
            parsed_data.get('date', ''),
            parsed_data.get('ifsc_code', ''),
            parsed_data.get('amount_in_words', ''),
            parsed_data.get('amount_in_digits', ''),
            parsed_data.get('payer', ''),
            parsed_data.get('account_number', ''),
            parsed_data.get('cheque_number', ''),
            parsed_data.get('image_path', '')
        )

        cursor.execute(insert_query, record_to_insert)
        connection.commit()
        logger.info("Record inserted successfully into parsed_cheques_table")

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
