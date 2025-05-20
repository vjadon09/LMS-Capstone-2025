let selectedBook = null;
let books = [];

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

// Function to search the books dynamically
function searchBooks() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  if (query === "") {
      clearSearchResults();
      selectedBook = null;
      document.getElementById('bookDetails').innerHTML = '';
      deleteButtonDisable();
  } else {
      const filteredBooks = books.filter(book => 
          book.title.toLowerCase().includes(query) ||
          book.author.toLowerCase().includes(query) ||
          book.isbn.toLowerCase().includes(query)
      );
      displayBooks(filteredBooks);
  }
}

// Function to display the list of books as buttons
function displayBooks(booksToDisplay) {
  const bookList = document.getElementById('bookList');
  bookList.innerHTML = '';
  if (booksToDisplay.length === 0) {
      bookList.innerHTML = '<li class="list-group-item">No books found.</li>';
  } else {
      booksToDisplay.forEach(book => {
        const listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        
        // Create a button for each book
        const bookButton = document.createElement('button');
        bookButton.classList.add('btn', 'btn-custom-search', 'w-100', 'p-1');
        if (book.format === "Audio"){bookButton.innerHTML = `<h5>${book.title}🎧</h5> <p>By: ${book.author}</p> <p><i>${book.genre}</i></p>`;}
        else {bookButton.innerHTML = `<h5>${book.title}📖</h5> <p>By: ${book.author}</p> <p><i>${book.genre}</i></p>`;}
        
        bookButton.addEventListener('click', () => {
            selectedBook = book;
            displayBookDetails(book);  
            clearSearchResults(); 
            deleteButtonEnable();
        });
        
        // Append the button to the list item
        listItem.appendChild(bookButton);
        bookList.appendChild(listItem);
      });
  }
}

// Function to display detailed book information
function displayBookDetails(book) {
  const bookDetailsDiv = document.getElementById('bookDetails');
  let length;
  if (book.format === "Audio"){length = `<strong>Number of Minutes:</strong> ${book.numOfMins}`} 
  else{length = `<strong>Page Length:</strong> ${book.pageNumber}`;}
  bookDetailsDiv.innerHTML = `
      <h5>${book.title}</h5>
      <p><strong>Author:</strong> ${book.author}</p>
      <p><strong>ISBN:</strong> ${book.isbn}</p>
      <p><strong>Format:</strong> ${book.format}</p>
      <p><strong>Genre:</strong> ${book.genre}</p>
      <p><strong>Kid Friendly:</strong> ${book.kidFriendly ? "Yes" : "No"}</p>
      <p><strong>Rating:</strong> ${book.rating} ⭐</p>
      <p><strong>Publisher:</strong> ${book.publisher}</p>
      <p>${length}</p>
      <p><strong>Number of copies:</strong> ${book.numCopies}</p>
      <p><strong>Status:</strong> ${book.status}</p>
      <p><strong>Description:</strong> ${book.description}</p>
  `;
  console.log(book)
}

function clearSearchResults() {
  const bookList = document.getElementById('bookList');
  bookList.innerHTML = ''; 
}

function deleteButtonEnable(){
  const deleteButton = document.getElementById('deleteButton');
  deleteButton.disabled = false;
}

function deleteButtonDisable(){
  const deleteButton = document.getElementById('deleteButton');
  deleteButton.disabled = true;
}

window.onload = function() {
  deleteButtonDisable();
  fetchBooks();
}

function validateForm() {
  let isValid = true;
  const searchInput = document.getElementById("searchInput").value.trim();
  const errorMessageDiv = document.getElementById("errorMessage");

  return isValid;
}

async function deleteBook() {
  event.preventDefault();
  var myModal = new bootstrap.Modal(document.getElementById('successModal'));
  const formIsValid = validateForm();
  if (formIsValid) {
    try {
      const response = await fetch(`/catalog/delete-books/${selectedBook.isbn}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const result = await response.json();
        document.getElementById('modal-body').innerHTML = formatModal(false);
        myModal.show();
        const closeButton = document.querySelector('.btn-close');
        closeButton.addEventListener('click', function () {
          document.getElementById('bookDetails').innerHTML = '';
          window.location.href = "/catalog/remove-item"; 
        });
      } else {
        document.getElementById('modal-body').innerHTML = formatModal(true);
        myModal.show();
      }
    } catch (error) {
      console.error("Error deleting book:", error);
    }
  }
}

function cancel(){
  location.href = "/catalog/edit_inventory";
}

function formatModal(error){
  let modalBody;
  if (error){
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">❎</p></div>
                <div class="row"><p class="text-center fs-5">Form submission failed!</p></div>
                <div class="row"><p class="text-center">Please try again.</p></div>`
    
  } else{
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">✅</p></div>
                <div class="row"><p class="text-center fs-5">Successfully submited!</p></div>`
  }
  return modalBody
}

document.getElementById("deleteBookForm").addEventListener("submit", deleteBook);