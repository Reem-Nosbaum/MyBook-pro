from pymongo import MongoClient

# חיבור ל-MongoDB דרך השירות "mongodb" שמוגדר ב-docker-compose.yml
client = MongoClient("mongodb://mongodb:27017/")
db = client["book_tracker"]
books_collection = db["books"]

# פונקציה להוספת ספר
def add_book_to_db(book):
    result = books_collection.insert_one(book)
    book["_id"] = str(result.inserted_id)  # ממיר את ObjectId למחרוזת
    return book

# פונקציה לעדכון סטטוס ספר
def update_book_status(book_id, status):
    result = books_collection.update_one(
        {"id": book_id}, {"$set": {"status": status}}
    )
    return result.modified_count

# פונקציה לקבלת כל הספרים
def get_all_books():
    return list(books_collection.find({}, {"_id": 0}))  # לא מציג את ה-_id

# פונקציה לבדוק אם ספר קיים
def book_exists(book_id):
    return books_collection.find_one({"id": book_id}) is not None

def delete_book_from_db(book_id):
    result = books_collection.delete_one({"id": book_id})
    return result.deleted_count
