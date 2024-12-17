const BACKEND_URL = "http://127.0.0.1:5000"; // כתובת ה-Backend הגלובלית

// פונקציה לחיפוש ספרים
function searchBooks() {
    const query = document.getElementById("search-query").value;
    if (!query) {
        alert("Please enter a search query!");
        return;
    }

    fetch(`${BACKEND_URL}/search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById("search-results");
            resultsContainer.innerHTML = ""; // ניקוי התוצאות הקודמות
            data.forEach(book => {
                const bookDiv = document.createElement("div");
                bookDiv.className = "book";

                bookDiv.innerHTML = `
                    <h3>${book.title}</h3>
                    <p>Authors: ${book.authors.join(", ")}</p>
                    <img src="${book.thumbnail}" alt="No Image Available">
                    <button onclick="addBook('${book.id}', '${book.title}', '${book.authors}')">Add to My List</button>
                `;
                resultsContainer.appendChild(bookDiv);
            });
        })
        .catch(error => console.error("Error fetching search results:", error));
}

// פונקציה להוספת ספר לרשימה
function addBook(id, title, authors) {
    fetch(`${BACKEND_URL}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, title: title, authors: authors.split(", ") })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadBooks(); // טוען מחדש את רשימת הספרים
    })
    .catch(error => console.error("Error adding book:", error));
}

// פונקציה לטעינת רשימת הספרים
function loadBooks() {
    fetch(`${BACKEND_URL}/books`)
        .then(response => response.json())
        .then(data => {
            const bookListContainer = document.getElementById("book-list");
            bookListContainer.innerHTML = ""; // ניקוי הרשימה הקודמת
            data.forEach(book => {
                const bookDiv = document.createElement("div");
                bookDiv.className = "book";

                bookDiv.innerHTML = `
                    <h3>${book.title}</h3>
                    <p>Status: ${book.status}</p>
                    <button onclick="markAsRead('${book.id}')">Mark as Read</button>
                    <button onclick="deleteBook('${book.id}')">Delete</button>
                `;
                bookListContainer.appendChild(bookDiv);
            });
        })
        .catch(error => console.error("Error loading books:", error));
}

// פונקציה לסימון ספר כ"נקרא"
function markAsRead(bookId) {
    fetch(`${BACKEND_URL}/mark_as_read/${bookId}`, {
        method: "PUT"
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadBooks(); // טוען מחדש את הרשימה
    })
    .catch(error => console.error("Error marking book as read:", error));
}

// פונקציה למחיקת ספר מהרשימה
function deleteBook(bookId) {
    fetch(`${BACKEND_URL}/delete/${bookId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        loadBooks(); // טוען מחדש את רשימת הספרים
    })
    .catch(error => console.error("Error deleting book:", error));
}

// טוען את רשימת הספרים בהתחלה
window.onload = loadBooks;
