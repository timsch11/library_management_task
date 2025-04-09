from flask import Flask, render_template, jsonify, make_response, request
import configparser
import requests
import logging
from flask_cors import CORS

from psycopg2 import pool
import psycopg2.extras

from dotenv import dotenv_values

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load the configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# read .env
db_secrets = dotenv_values(".env")

# setup connection pool for thread safety
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="library_management",
    user=db_secrets["DB_USER"],
    password=db_secrets["DB_PASSWORD"],
    host="localhost",
    port="5432"
)

del db_secrets

# Get the API key and URL from the configuration
try:
    GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
    GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
    logging.info("Gemini API configuration loaded successfully.")
except Exception as e:
    logging.error("Error reading config.ini: %s", e)
    GEMINI_API_KEY = None
    GEMINI_API_URL = None

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

@app.route('/api/borrower', methods=['GET'])
def get_borrower():
    """returns all borrowers when no name is specified"""
    borrower_name = request.args.get('name', default=-1)

    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        if borrower_name == -1:
            cur.execute("SELECT * FROM Borrower;")
        else:
            cur.execute(f"SELECT * FROM Borrower WHERE name=%s", (borrower_name,))

        borrowers = cur.fetchall()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        if borrowers == None:
            return make_response({"error": "Database querry gave no results"}, 400)

        # send books back to client (as a json)
        return jsonify(borrowers)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)

@app.route('/api/author', methods=['GET'])
def get_author():
    """returns all authors when no id is specified"""
    author_id = request.args.get('id', default=-1)

    # avoid sql injection
    try:
        int(author_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)
    
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        if author_id == -1:
            cur.execute("SELECT * FROM Author;")
        else:
            cur.execute(f"SELECT * FROM Author WHERE id={author_id}")

        authors = cur.fetchall()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        if authors == None:
            return make_response({"error": "Database querry gave no results"}, 400)

        # send books back to client (as a json)
        return jsonify(authors)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/publisher', methods=['GET'])
def get_publisher():
    """returns all publishers when no id is specified"""
    publisher_id = request.args.get('id', default=-1)

    # avoid sql injection
    try:
        int(publisher_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)
    
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        if publisher_id == -1:
            cur.execute("SELECT * FROM Publisher;")
        else:
            cur.execute(f"SELECT * FROM Publisher WHERE id={publisher_id}")

        publishers = cur.fetchall()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        if publishers == None:
            return make_response({"error": "Database querry gave no results"}, 400)

        # send books back to client (as a json)
        return jsonify(publishers)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/genre', methods=['GET'])
def get_genre():
    """returns all genres when no id is specified"""
    genre_id = request.args.get('id', default=-1)

    # avoid sql injection
    try:
        int(genre_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)
    
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        if genre_id == -1:
            cur.execute("SELECT * FROM Genre;")
        else:
            cur.execute(f"SELECT * FROM Genre WHERE id={genre_id}")

        genres = cur.fetchall()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        if genres == None:
            return make_response({"error": "Database querry gave no results"}, 400)

        # send books back to client (as a json)
        return jsonify(genres)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/books', methods=['GET'])
def get_books():
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("SELECT * FROM Books;")
        books = cur.fetchall()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        if books == None:
            return make_response({"error": "Database querry gave no results"}, 500)

        # send books back to client (as a json)
        return jsonify(books)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/removeBorrowers', methods=['POST'])
def remove_borrowers():
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("DELETE FROM Borrower;")
        conn.commit()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        return jsonify({"status": "success"})
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
# In app.py
@app.route('/api/borrow', methods=['POST'])
def borrow():
    # Get JSON data from request body instead of form data
    data = request.json
    
    if not data:
        return make_response({"error": "No JSON data provided"}, 400)
    
    book_id = data.get('bookid')
    borrower_name = data.get('name')
    borrow_date = data.get('borrowDate')
    return_date = data.get('returnDate')
    
    logging.info(f"Borrowing book: {book_id} by {borrower_name}")
    logging.info(f"Dates: borrow={borrow_date}, return={return_date}")

    if not borrower_name:
        return make_response({"error": "No borrower name is set"}, 400)
    
    if not book_id:
        return make_response({"error": "No book id is set"}, 400)
    
    if not borrow_date:
        return make_response({"error": "No borrowDate is set"}, 400)
    
    if not return_date:
        return make_response({"error": "No returnDate is set"}, 400)
        
    # Rest of the function remains the same...
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("INSERT INTO Borrower (name) SELECT %s WHERE NOT EXISTS (SELECT 1 FROM Borrower WHERE name = %s)", (borrower_name, borrower_name))
        cur.execute("UPDATE Books SET borrower = %s, borrowDate = %s, returnDate = %s WHERE id = %s", (borrower_name, borrow_date, return_date, book_id))
        conn.commit()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        return jsonify({"status": "success"})
    
    except Exception as exc:
        raise exc
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/return', methods=['POST'])
def return_book():
    # Get JSON data from request body instead of form data
    data = request.json
    
    if not data:
        return make_response({"error": "No JSON data provided"}, 400)
    
    book_id = data.get('bookid')

    if not book_id:
        return make_response({"error": "No book id is set"}, 400)
    
    # borrow connection from pool and get cursor
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("UPDATE Books SET borrowDate = NULL, returnDate = NULL WHERE id = %s RETURNING borrower;", (book_id, ))
        response = cur.fetchall()
        cur.execute("DELETE FROM Borrower WHERE name = %s;", ((response[0]["borrower"],)))
        conn.commit()

        cur.close()

        # Return connection to pool
        db_pool.putconn(conn)

        return jsonify({"status": "success"})
    
    except Exception as exc:
        raise exc
        return make_response({"error": str(exc)}, 500)
    

# API route to fetch description from Gemini API
@app.route('/api/description', methods=['GET'])
def get_description():
    entity_name = request.args.get('name')
    logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

    if not entity_name:
        logging.warning("Missing entity name in request.")
        return jsonify({'error': 'Missing entity name'}), 400

    if not GEMINI_API_URL or not GEMINI_API_KEY:
        logging.error("Gemini API configuration missing.")
        return jsonify({'error': 'Server configuration error'}), 500

    # Prepare the JSON payload with explicit instructions
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Provide a detailed description of '{entity_name}'"
                            "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
                            "Do not include any concluding remarks or questions."
                            "Do not mention any Note at the end about not including concluding remarks or questions."
                        )
                    }
                ]
            }
        ]
    }

    # Construct the API URL with the API key as a query parameter
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Log the API URL and payload for debugging
    #logging.debug(f"API URL: {api_url_with_key}")
    logging.debug(f"Payload: {payload}")

    try:
        # Make the POST request to the Gemini API
        response = requests.post(
            api_url_with_key,  # Include the API key in the URL
            headers=headers,
            json=payload,
            timeout=10  # seconds
        )
        logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

        if response.status_code != 200:
            logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return jsonify({
                'error': 'Failed to fetch description from Gemini API',
                'status_code': response.status_code,
                'response': response.text
            }), 500

        response_data = response.json()
        # Extract the description from the response
        description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
        logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

        return jsonify({'description': description})

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during Gemini API request: {e}")
        return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
    except ValueError as e:
        logging.error(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
