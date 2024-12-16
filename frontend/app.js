const backendURL = "http://10.1.0.41:5001/";

// חיפוש ספרים ב-Google Books ושמירתם
async function searchBooks() {
  const query = document.getElementById("searchQuery").value;
  if (!query) {
    alert("Please enter a search query!");
    return;
  }

  try {
    const response = await fetch(`${backendURL}/books/search?q=${query}`);
    const data = await response.json();

    if (data.message) {
      document.getElementById("searchResults").innerHTML = `
                <p>${data.message}</p>
                <pre>${JSON.stringify(data.data, null, 2)}</pre>
            `;
    } else {
      document.getElementById(
        "searchResults"
      ).innerHTML = `<p>Error: ${data.error}</p>`;
    }
  } catch (error) {
    console.error("Error fetching books:", error);
  }
}

// שליפת כל הספרים השמורים
async function fetchSavedBooks() {
  try {
    const response = await fetch(`${backendURL}/books`);
    const books = await response.json();

    let booksHTML = "";
    books.forEach((book) => {
      booksHTML += `
                <div>
                    <h3>${book.title}</h3>
                    <p>Authors: ${book.authors.join(", ")}</p>
                    <p>Published: ${book.publishedDate || "N/A"}</p>
                    <p>Status: ${book.status}</p>
                </div>
                <hr>
            `;
    });

    document.getElementById("savedBooks").innerHTML =
      booksHTML || "<p>No books saved yet.</p>";
  } catch (error) {
    console.error("Error fetching saved books:", error);
  }
}
