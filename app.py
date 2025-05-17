from flask import Flask, render_template, jsonify, make_response, request
import configparser
import requests
import logging
from flask_cors import CORS

from neo4j import GraphDatabase

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

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

db = Neo4jConnector("bolt://localhost:7687", db_secrets["DB_NEO_USER"], db_secrets["DB_PASSWORD"])

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

    try:
        if borrower_name == -1:
            query = "MATCH (borrower:Borrower) RETURN borrower.id AS id, borrower.name AS name;"
        else:
            query = "MATCH (borrower:Borrower) WHERE borrower.name = $name RETURN borrower.id AS id, borrower.name AS name;"

        borrowers = db.run_query(query, {'name': borrower_name})
        

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
        author_id = int(author_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)

    try:
        if author_id == -1:
            query = "MATCH (author:Author) RETURN author.id AS id, author.name as name, author.description AS description;"
        else:
            query = "MATCH (author:Author) WHERE author.id = $author_id RETURN author.id AS id, author.name as name, author.description AS description;"

        authors = db.run_query(query, {'author_id': author_id})

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
        publisher_id = int(publisher_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)

    try:
        if publisher_id == -1:
            query = "MATCH (publisher:Publisher) RETURN publisher.id AS id, publisher.name as name, publisher.description AS description;"
        else:
            query = "MATCH (publisher:Publisher) WHERE publisher.id = $publisher_id RETURN publisher.id AS id, publisher.name as name, publisher.description AS description;"


        publishers = db.run_query(query, {'publisher_id': publisher_id})

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
        genre_id = int(genre_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)

    try:
        if genre_id == -1:
            query = "MATCH (genre:Genre) RETURN genre.id AS id, genre.name as name, genre.description AS description;"
            genres = db.run_query(query)
        else:
            query = "MATCH (genre:Genre) WHERE genre.id = $genre_id RETURN genre.id AS id, genre.name as name, genre.description AS description;"
            genres = db.run_query(query, {'genre_id': genre_id})

        if genres == None:
            return make_response({"error": "Database querry gave no results"}, 400)
        
        logging.info(genres)
        # send books back to client (as a json)
        return jsonify(genres)
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)

@app.route('/api/books', methods=['GET'])
def get_books():
    book_id = request.args.get('id', default=-1)

    # avoid sql injection
    try:
        book_id = int(book_id)
    except Exception as exc:
        return make_response({"error": "invalid id header"}, 400)
    
    try:
        # complete Cypher query to fetch books with all necessary properties
        if book_id != -1:
            query = """
            MATCH (book:Book)
            WHERE book.id = $book_id
            OPTIONAL MATCH (book)-[:WRITTEN_BY]->(author:Author)
            OPTIONAL MATCH (book)-[:PUBLISHED_BY]->(publisher:Publisher)
            OPTIONAL MATCH (book)-[:OF_GENRE]->(genre:Genre)
            OPTIONAL MATCH (book)-[:BORROWED_BY]->(borrower:Borrower)
            RETURN book.id AS id, 
                book.title AS title, 
                book.description AS description,
                book.present AS present,
                book.borrowdate AS borrowdate,
                book.returndate AS returndate,
                book.borrower AS borrower,
                author.id AS author,
                author.name AS author_name,
                publisher.id AS publisher, 
                publisher.name AS publisher_name,
                genre.id AS genre,
                genre.name AS genre_name,
                borrower.name AS borrower_name
            """
            
            books = db.run_query(query, {'book_id': book_id})

        else: 
            query = """
            MATCH (book:Book)
            OPTIONAL MATCH (book)-[:WRITTEN_BY]->(author:Author)
            OPTIONAL MATCH (book)-[:PUBLISHED_BY]->(publisher:Publisher)
            OPTIONAL MATCH (book)-[:OF_GENRE]->(genre:Genre)
            OPTIONAL MATCH (book)-[:BORROWED_BY]->(borrower:Borrower)
            RETURN book.id AS id, 
                book.title AS title, 
                book.description AS description,
                book.present AS present,
                book.borrowdate AS borrowdate,
                book.returndate AS returndate,
                book.borrower AS borrower,
                author.id AS author,
                author.name AS author_name,
                publisher.id AS publisher, 
                publisher.name AS publisher_name,
                genre.id AS genre,
                genre.name AS genre_name,
                borrower.name AS borrower_name
            """
            
            books = db.run_query(query)

        if books is None:
            return make_response({"error": "Database query gave no results"}, 500)

        # send books back to client (as a json)
        return jsonify(books)
    
    except Exception as exc:
        logging.error(f"Error fetching books: {exc}")
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/removeBorrowers', methods=['POST'])
def remove_borrowers():
    try:
        query = "MATCH (a:Book)-[r:BORROWED_BY]->(b:Borrower) DELETE r;"
        db.run_query(query)

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
    
    book_id = int(data.get('bookid'))
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

    try:
        # First make sure the borrower exists, create if not exists
        create_borrower_query = """
        MERGE (b:Borrower {name: $borrower_name})
        ON CREATE SET b.id = apoc.create.uuid()
        RETURN b
        """
        db.run_query(create_borrower_query, {'borrower_name': borrower_name})
        
        # Then update the book and create the BORROWED_BY relationship
        borrow_book_query = """
        MATCH (book:Book {id: $book_id})
        MATCH (borrower:Borrower {name: $borrower_name})
        SET book.present = false, 
            book.borrowdate = $borrow_date, 
            book.returndate = $return_date,
            book.borrower = $borrower_name
        CREATE (book)-[r:BORROWED_BY]->(borrower)
        RETURN book
        """
        
        db.run_query(borrow_book_query, {
            'book_id': book_id, 
            'borrower_name': borrower_name, 
            'borrow_date': borrow_date, 
            'return_date': return_date
        })

        return jsonify({"status": "success"})
    
    except Exception as exc:
        return make_response({"error": str(exc)}, 500)
    
@app.route('/api/return', methods=['POST'])
def return_book():
    # Get JSON data from request body instead of form data
    data = request.json
    
    if not data:
        return make_response({"error": "No JSON data provided"}, 400)
    
    book_id = int(data.get('bookid'))

    if not book_id:
        return make_response({"error": "No book id is set"}, 400)

    try:
        # First delete the BORROWED_BY relationship
        delete_relationship_query = """
        MATCH (book:Book {id: $book_id})-[r:BORROWED_BY]->(borrower:Borrower) 
        DELETE r
        RETURN count(r) as deleted_count
        """
        result = db.run_query(delete_relationship_query, {'book_id': book_id})
        
        # Check if a relationship was actually deleted
        if not result or result[0]['deleted_count'] == 0:
            logging.warning(f"No borrowing relationship found for book ID: {book_id}")
        
        # Update the book properties to mark it as returned
        update_book_query = """
        MATCH (book:Book {id: $book_id})
        SET book.present = true,
            book.borrowdate = null,
            book.returndate = null,
            book.borrower = null
        """
        db.run_query(update_book_query, {'book_id': book_id})
        
        logging.info(f"Book {book_id} has been returned successfully")
        return jsonify({"status": "success"})
    
    except Exception as exc:
        logging.error(f"Error returning book: {exc}")
        return make_response({"error": str(exc)}, 500)
    

# API route to fetch description from Gemini API
@app.route('/api/description', methods=['GET'])
def get_description():
    entity_type = request.args.get('type')
    entity_name = request.args.get('name')
    logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

    
    if not entity_name:
        logging.warning("Missing entity name in request.")
        return jsonify({'error': 'Missing entity name'}), 400

    ### look into db for cached description

    try:
        if entity_type == "Books":
            query = "MATCH (book:Book) WHERE book.title = $entity_name RETURN book.description AS description;"
        else:
            query = f"MATCH (el:{entity_type}) WHERE el.name = $entity_name RETURN el.description AS description;"
        
        data = db.run_query(query, {'entity_name': entity_name})
        logging.info("length", len(data), data)
        description = data[0]["description"]

        # consider that an actual description
        if len(description) > 10:
            logging.info("Found existing description in db cache.")

            return jsonify({'description': description})
    
    except Exception as exc:
        logging.exception("Exception")
        return make_response({"error": str(exc)}, 500)

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

        if entity_type == "Books":
            query = "MATCH (book:Book) WHERE book.title = $entity_name SET book.description = $description;"
        else:
            query = f"MATCH (el:{entity_type}) WHERE el.name = $entity_name SET el.description = $description;"
        
        data = db.run_query(query, {'entity_name': entity_name, 'description': description})

        logging.info("Successfully stored description in db.")
    
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
