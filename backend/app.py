from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from models import add_book_to_db, update_book_status, get_all_books, book_exists, delete_book_from_db

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

# חיפוש ספרים ב-Google Books API
@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(api_url)
    if response.status_code == 200:
        books = response.json().get('items', [])
        result = [
            {
                "id": book["id"],
                "title": book["volumeInfo"].get("title", "No Title"),
                "authors": book["volumeInfo"].get("authors", []),
                "description": book["volumeInfo"].get("description", "No Description"),
                "thumbnail": book["volumeInfo"].get("imageLinks", {}).get("thumbnail", "")
            }
            for book in books
        ]
        return jsonify(result), 200
    return jsonify({"error": "Failed to fetch data from Google Books API"}), 500


# הוספת ספר לרשימה האישית
@app.route('/add', methods=['POST'])
def add_book():
    data = request.json
    if not data or "title" not in data or "id" not in data:
        return jsonify({"error": "Invalid data"}), 400

    if book_exists(data["id"]):
        return jsonify({"error": "Book already exists"}), 400

    book = {
        "id": data["id"],
        "title": data["title"],
        "authors": data.get("authors", []),
        "status": "unread"
    }
    saved_book = add_book_to_db(book)  # קבלת הספר עם ה-ID המומר
    return jsonify({"message": "Book added successfully", "book": saved_book}), 201


# סימון ספר כ"נקרא"
@app.route('/mark_as_read/<book_id>', methods=['PUT'])
def mark_as_read(book_id):
    updated = update_book_status(book_id, "read")
    if updated:
        return jsonify({"message": "Book marked as read"}), 200
    return jsonify({"error": "Book not found"}), 404


# קבלת כל הספרים
@app.route('/books', methods=['GET'])
def get_books():
    books = get_all_books()
    return jsonify(books), 200

@app.route('/delete/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    deleted = delete_book_from_db(book_id)  # קריאה לפונקציה החדשה
    if deleted:
        return jsonify({"message": "Book deleted successfully"}), 200
    return jsonify({"error": "Book not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
