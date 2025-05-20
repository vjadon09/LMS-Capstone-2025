window.onload = function () {
    fetchBooks();
};

let books = [];
let filteredBooks = books;

async function fetchBooks() {
    try {
        const response = await fetch('/catalog/books/');
        if (response.ok) {
            const bookData = await response.json();
            books = bookData;
            displayBooks(books);
        } else {
            console.error('Error fetching books:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayBooks(filteredBooks) {
    const bookGrid = document.getElementById("bookGrid");
    bookGrid.classList.remove("d-none");
    bookGrid.innerHTML = "";

    filteredBooks.forEach((book) => {
        const bookCard = document.createElement("div");
        bookCard.className = "col";
        bookCard.innerHTML = `
            <button type="submit" class="h-100 w-100" style="border: none; background:none;" 
                onclick="displayBookDetails('${book.isbn}')">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${book.title}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${book.author}</h6>
                        <p class="card-text"><strong>ISBN:</strong> ${book.isbn}</p>
                        <p class="card-text"><strong>Genre:</strong> ${book.genre}</p>
                        <p class="card-text"><strong>Format:</strong> ${book.format}</p>
                        <p class="card-text"><strong>Availability:</strong> ${book.status}</p>
                        <p class="card-text"><strong>Kid Friendly:</strong> ${book.kidFriendly ? "Yes" : "No"}</p>
                        <p class="card-text"><strong>Copies:</strong> ${book.numCopies}</p>
                    </div>
                </div>
            </button>
        `;
        bookGrid.appendChild(bookCard);
    });
}

// Function to filter books
function filterBooks() {
    const genreFilter = document.getElementById("genreFilter").value;
    const availabilityFilter = document.getElementById("availabilityFilter").value;
    const kidFriendlyFilter = document.getElementById("kidFriendlyFilter").checked;
    const quantityFilter = document.getElementById("quantityFilter").value;
    const quantityValue = quantityFilter === "" ? null : parseInt(quantityFilter, 10);

    filteredBooks = books.filter(book => {
        return (
            (genreFilter === "" || book.genre === genreFilter) &&
            (availabilityFilter === "" || (availabilityFilter === "Available" && book.status === "Available") || 
             (availabilityFilter === "Not Available" && book.status === "Not Available")) &&
            (!kidFriendlyFilter || book.kidFriendly) &&
            (quantityValue === null || book.numCopies === quantityValue)
        );
    });

    displayBooks(filteredBooks);
}

// Function to search books
function searchBooks() {
    let query = document.getElementById("searchInput").value;

    if (!isNaN(query)) {
        query = query.trim(); // Handle number as a string (removing spaces if needed)
    } else {
        query = query.toLowerCase(); // If it's not a number, apply toLowerCase
    }

    const filteredBooks = books.filter(book =>
        book.title.toLowerCase().includes(query) ||
        book.author.toLowerCase().includes(query) ||
        book.isbn.includes(query)
    );
    displayBooks(filteredBooks);
}

async function displayBookDetails(bookISBN) {
    const book = books.find(b => b.isbn === bookISBN);
    if (!book) return;
    console.log(book);
    const bookGrid = document.getElementById("bookGrid");
    bookGrid.classList.add("d-none");

    const bookDetailsDiv = document.getElementById("bookDetails");
    bookDetailsDiv.classList.remove("d-none");
    const imageUrl = await getImage(book.isbn);

    bookDetailsDiv.innerHTML = `
        <div class="card shadow-sm p-4 rounded">
            <h2 class="text-center mb-4">${book.title}</h2>
            <div class="row">
                <div class="col-md-3">
                    <p><strong>Author:</strong> ${book.author}</p>
                    <p><strong>ISBN:</strong> ${book.isbn}</p>
                    <p><strong>Genre:</strong> ${book.genre}</p>
                    <p><strong>Number of Copies:</strong> ${book.numCopies}</p>
                    <p><strong>Rating:</strong> ${book.rating}</p>
                    <p><strong>Kid Friendly:</strong> ${book.kidFriendly ? "Yes" : "No"}</p>
                    <p><strong>Publisher:</strong> ${book.publisher}</p>
                    <p><strong>Status:</strong> ${book.status}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Description:</strong> ${book.description}</p>
                    <p><strong>Format:</strong> ${book.format}</p>
                    <p><strong>Number of Minutes:</strong> ${book.numOfMins}</p>
                    <p><strong>Page Number:</strong> ${book.pageNumber}</p>
                </div>
                <div class="col-md-3">
                    <img class="img-fluid rounded-4" src="${imageUrl}" alt="${book.title} Book Cover">
                </div>
                <div class="col-12 mt-4">
                  <h4 class="text-center mb-4">View Content 📟</h4>
                  ${setupContentFormat(book.format, book.title)}
                </div>
            </div>
            <button class="btn btn-primary mt-4 custom-back-btn" onclick="closeAndShowBooks()">Back</button>
        </div>
    `;
    
    if (book.format === "eBook"){
      await getePubContent(book.isbn);

      document.getElementById("prev").addEventListener("click", () => {
        if (rendition) rendition.prev();
      });

      document.getElementById("next").addEventListener("click", () => {
        if (rendition) rendition.next();
      });
      
    } else {
      await getAudioContent(book.isbn);
    }
}

function closeAndShowBooks(){
    const bookGrid = document.getElementById("bookGrid");
    bookGrid.classList.remove("d-none");

    const bookDeets = document.getElementById("bookDetails");
    bookDeets.classList.add("d-none");
}

// change this to an API call to get the book cover
async function getImage(isbn){
    try {
        const coverResponse = await fetch(`/catalog/serve-book-cover/${isbn}`);
        if (coverResponse.ok) {
            let blob = await coverResponse.blob();
            let coverBlob = new Blob([blob], { type: "image/jpg" });
            let blobUrl = URL.createObjectURL(coverBlob);
            return blobUrl;
        }
    } catch (coverError) {
        console.error(`Error fetching cover for ISBN: ${isbn}`, coverError);
    }
    return "";
}

// get the ebook
async function getePubContent(isbn){
  try {
    const response = await fetch(`/catalog/file/${isbn}/eBook`);
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            let blob = await response.blob();
            console.log("Received EPUB Blob:", blob);

            let epubBlob = new Blob([blob], { type: "application/epub+zip" });
            let blobUrl = URL.createObjectURL(epubBlob);
            console.log("Created Blob URL:", blobUrl);

            const epubBook = ePub(blobUrl, { openAs: "epub" });
            console.log("EPUB Object Created:", epubBook);

            epubBook.ready
                .then(() => console.log("EPUB is ready!"))
                .catch(err => console.error("Error waiting for EPUB ready:", err));

            epubBook.opened
                .then(() => console.log("EPUB fully opened!"))
                .catch(err => console.error("Error waiting for EPUB opened:", err));

            rendition = epubBook.renderTo("epub-container", {
                width: "100%",
                height: "100%"
            });
            rendition.display();
  } catch (error) {
    console.error(`Error fetching file for ISBN: ${isbn}`, error);
  }
  return ""
}

//get the audio book
async function getAudioContent(isbn){
  try {
    const audioPlayer = document.getElementById("audio-player");
    const container = document.getElementById("container");
    const response = await fetch(`/catalog/file/${isbn}/Audio`);
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            container.innerText = "Loading audiobook...";

            let audioBlob = await response.blob();
            let audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = audioUrl;

            // Once the audio is loaded, set the container text to empty
            audioPlayer.oncanplaythrough = () => {
                container.innerText = "";
            };

            console.log("Audiobook loaded and ready to play!");

  } catch (error){
    console.error(`Error fetching file for ISBN: ${isbn}`, error);
  }
}

//function to create the html based on audio or ebook
function setupContentFormat(format, title){
  let mediaBody;
  if (format === "Audio"){
    mediaBody = `<div id="audio-player-container" class="w-100" style="border: none;">
                    <div id="container">Loading audiobook ...</div>
                    <audio id="audio-player" controls class="w-100">
                        <!-- Audio will be dynamically added -->
                    </audio>
                </div>`
  }
  else {
    mediaBody = `<div id="epub-container" class="w-100 epub-area" style="border: 1px solid rgba(184, 184, 184, 0.389); height: 100vh; border-radius: 30px; box-shadow: 0px 0px 10px rgba(178, 178, 178, 0.3)"></div>
                  <div class="modal-footer justify-content-center">
                      <button id="prev" class="btn" style="font-size: 30px;">⏮️</button>
                      <button id="next" class="btn" style="font-size: 30px;">⏩</button>
                  </div>`;
  }
  return mediaBody;
}