from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests
from bson.objectid import ObjectId
import os


app = Flask(__name__)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/book_tracker')
client = MongoClient(MONGO_URI)
db = client['book_tracker']
books_collection = db['books']

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Book Tracker API"})

@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Please provide a search term"}), 400

    response = requests.get(f"{GOOGLE_BOOKS_API}?q={query}")
    if response.status_code == 200:
        data = response.json()
        books = []

        for item in data.get('items', []):
            book_info = {
                "title": item['volumeInfo'].get('title'),
                "authors": item['volumeInfo'].get('authors', []),
                "publishedDate": item['volumeInfo'].get('publishedDate'),
                "description": item['volumeInfo'].get('description'),
                "status": "unread"
            }
            result = books_collection.insert_one(book_info)
            book_info['_id'] = str(result.inserted_id)
            books.append(book_info)

        return jsonify({"message": "Books saved successfully", "data": books}), 200

    return jsonify({"error": "Failed to fetch data from Google Books API"}), 500

@app.route('/books', methods=['GET'])
def get_books():
    all_books = list(books_collection.find({}, {'_id': 0}))
    return jsonify(all_books), 200


@app.route('/books/<title>/status', methods=['PUT'])
def update_book_status(title):
    """
    Update the 'status' field of a book (read/unread).
    """
    new_status = request.json.get('status')
    if new_status not in ['read', 'unread']:
        return jsonify({"error": "Invalid status. Use 'read' or 'unread'."}), 400

    result = books_collection.update_one(
        {"title": title},
        {"$set": {"status": new_status}}
    )
    if result.matched_count:
        return jsonify({"message": f"Book '{title}' status updated to '{new_status}'"}), 200
    return jsonify({"error": f"Book '{title}' not found"}), 404

@app.route('/books/<identifier>', methods=['DELETE'])
def delete_book(identifier):
    """
    Delete a book by title or ID.
    """
    try:
        # נסה למחוק לפי ObjectId
        if ObjectId.is_valid(identifier):
            result = books_collection.delete_one({"_id": ObjectId(identifier)})
        else:
            # אם לא ObjectId, נסה למחוק לפי כותרת
            result = books_collection.delete_one({"title": identifier})

        if result.deleted_count:
            return jsonify({"message": f"Book '{identifier}' deleted successfully"}), 200
        return jsonify({"error": f"Book '{identifier}' not found"}), 404

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/books/search_local', methods=['GET'])
def search_local_books():
    """
    Search books stored in MongoDB by title or author (partial match).
    """
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')

    # בניית תנאי החיפוש
    search_filter = {}
    if title_query:
        search_filter["title"] = {"$regex": title_query, "$options": "i"}  # חיפוש חלקי לפי כותרת
    if author_query:
        search_filter["authors"] = {"$regex": author_query, "$options": "i"}  # חיפוש חלקי לפי מחבר

    # שליפת התוצאות מהדאטהבייס
    books = list(books_collection.find(search_filter, {'_id': 0}))
    return jsonify(books), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
