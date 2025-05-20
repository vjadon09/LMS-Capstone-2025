let selectedBook = null;
let books = [];

function previewImage(event) {
  const imagePreview = document.getElementById('imagePreview');
  const file = event.target.files[0];
  
  if (file) {
      // Create a URL for the selected image file
      const reader = new FileReader();
      reader.onload = function() {
          imagePreview.src = reader.result;  // Set the source of the preview image
          imagePreview.style.display = 'block';  // Display the image
      }
      reader.readAsDataURL(file);  // Read the image file as data URL
  }
}

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

function searchBooks() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    if (query === "") {
        clearSearchResults();
        selectedBook = null;
        document.getElementById('bookDetails').style.display = 'none';
        document.getElementById('modifyBookForm').style.display = 'none';
        modifyButtonDisable();
    } else {
        const filteredBooks = books.filter(book =>
            book.title.toLowerCase().includes(query) ||
            book.author.toLowerCase().includes(query) ||
            book.isbn.toLowerCase().includes(query)
        );
        displayBooks(filteredBooks);
    }
}

function displayBooks(booksToDisplay) {
    const bookList = document.getElementById('bookList');
    bookList.innerHTML = '';
    booksToDisplay.forEach(book => {
        const listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        const bookButton = document.createElement('button');
        bookButton.classList.add('btn', 'btn-custom-search', 'w-100', 'p-1');
        if (book.format === "Audio"){bookButton.innerHTML = `<h5>${book.title}🎧</h5> <p>By: ${book.author}</p>`;}
        else {bookButton.innerHTML = `<h5>${book.title}📖</h5> <p>By: ${book.author}</p>`;}
        bookButton.addEventListener('click', () => {
            selectedBook = book;
            displayBookDetails(book);
            const modifyBookForm = document.getElementById('bookDetailsForm');
            if (modifyBookForm) {
                modifyBookForm.style.display = 'none';
            } else {
                console.error('bookDetailsForm not found');
            }
            clearSearchResults();
            modifyButtonEnable();
        });
        listItem.appendChild(bookButton);
        bookList.appendChild(listItem);
    });
}

async function displayBookDetails(book) {
    const bookDetailsDiv = document.getElementById('bookDetails');
    const imageUrl = await getImage(book.isbn);
    let length;
    if (book.format === "Audio"){
      length = `<strong>Number of Minutes:</strong> ${book.numOfMins}`
    } else{
      length = `<strong>Page Length:</strong> ${book.pageNumber}`;
    }
    bookDetailsDiv.innerHTML = `
      <div class="card shadow-sm p-4 rounded">
        <h5>${book.title}</h5>
        <div class="row">
          <div class="col-sm-6">
            <p><strong>Author:</strong> ${book.author}</p>
            <p><strong>ISBN:</strong> ${book.isbn}</p>
            <p><strong>Genre:</strong> ${book.genre}</p>
            <p><strong>Number of copies:</strong> ${book.numCopies}</p>
            <p><strong>Description:</strong> ${book.description}</p>
            <p><strong>Kid Friendly:</strong> ${book.kidFriendly ? "Yes" : "No"}</p>
            <p><strong>Format:</strong> ${book.format}</p>
            <p>${length}</p>
            <p><strong>Publisher:</strong> ${book.publisher}</p>
            <p><strong>Status:</strong> ${book.status}</p>
          </div>
          <div class="col-sm-6">
            <img class="img-fluid rounded-4" src="${imageUrl}" alt="${book.title} Book Cover">
          </div>
        </div>
        <button class="btn btn-custom-size mt-2" onclick="openModifyForm()">Modify</button>
      </div>
    `;
    document.getElementById('bookDetails').style.display = 'block';
}

function openModifyForm() {
    const modifyBookForm = document.getElementById('bookDetailsForm');
    const bookDeets = document.getElementById('bookDetails');

    if (modifyBookForm) {
        modifyBookForm.style.display = 'block';
        populateModifyForm(selectedBook);
    } else {
        console.error('bookDetailsForm not found');
    }

    if (bookDeets){
        bookDeets.style.display = "none";
    }
}

function populateModifyForm(book) {
    document.getElementById('title').value = book.title;
    document.getElementById('author').value = book.author;
    document.getElementById('isbn').value = book.isbn;
    document.getElementById('genre').value = book.genre;
    document.getElementById('numCopies').value = book.numCopies;
    document.getElementById('description').value = book.description;
    document.getElementById('kidFriendly').checked = book.kidFriendly;
    document.getElementById('format').value = book.format;
    document.getElementById('pageNumber').value = book.pageNumber;
    document.getElementById('numOfMins').value = book.numOfMins;
    document.getElementById('publisher').value = book.publisher;
    document.getElementById('status').value = book.status;

    if (book.format === "Audio"){
      console.log("Audio");
      document.getElementById("pageNumber").readOnly = true;
      document.getElementById("numOfMins").readOnly = false;
    }
    else{
      document.getElementById("numOfMins").readOnly = true;
      document.getElementById("pageNumber").readOnly = false;
    }
}

function modifyButtonEnable() {
    const modifyButton = document.getElementById('modifyButton');
    modifyButton.disabled = false;
}

function modifyButtonDisable() {
    const modifyButton = document.getElementById('modifyButton');
    modifyButton.disabled = true;
}

function clearSearchResults() {
    const modifyBookForm = document.getElementById("modifyBookForm");
    if (modifyBookForm) {
        modifyBookForm.reset();
    } else {
        console.error('modifyBookForm not found');
    }
}

window.onload = function() {
    modifyButtonDisable();
    fetchBooks();
}

function validateForm() {
    let isValid = true;
    const errorMessage = "This field is required";

    const formFields = document.querySelectorAll('#modifyBookForm input[required], #modifyBookForm textarea[required], #modifyBookForm select[required]');

    formFields.forEach(field => {
        const errorElement = document.getElementById(field.id + "-error");

        if (field.tagName.toLowerCase() === "select") {
            if (!field.value || field.value === "" || field.value === "Choose...") {
                isValid = false;
                if (!errorElement) {
                    const error = document.createElement('div');
                    error.id = field.id + "-error";
                    error.classList.add('text-danger', 'mt-2');
                    error.textContent = errorMessage;
                    field.parentElement.appendChild(error);
                }
            } else {
                if (errorElement) {
                    errorElement.remove();
                }
            }
        } else {
            if (!field.value.trim()) {
                isValid = false;
                if (!errorElement) {
                    const error = document.createElement('div');
                    error.id = field.id + "-error";
                    error.classList.add('text-danger', 'mt-2');
                    error.textContent = errorMessage;
                    field.parentElement.appendChild(error);
                }
            } else {
                if (errorElement) {
                    errorElement.remove();
                }
            }
        }
    });

    return isValid;
}

function modifyBook(event) {
    event.preventDefault();
    const formIsValid = validateForm();
    if (formIsValid) {
        //const data = Object.fromEntries(formData.entries());
        //data.kidFriendly = document.getElementById("kidFriendly").checked;
        const checkbox = document.getElementById('kidFriendly');
        if (checkbox.checked) {
          checkbox.value = "true";
        }else{
          checkbox.value = "false";
        }
        const formData = new FormData(document.getElementById("modifyBookForm"));
        formData.append("kidFriendly", checkbox.value);

        // Check book cover uploaded correctly
        const fileInput = document.getElementById('imageUpload');
        const file = fileInput.files[0];
        if (file) {
            if (!['image/jpeg', 'image/png'].includes(file.type)) {
                alert('Only JPG, PNG, or JPEG images are allowed for the book cover!');
                event.target.value = '';
                imagePreview.style.display = 'none';
                return;
            }
            const reader = new FileReader();
            reader.onloadend = function() {
              bookCoverValid = true;
            };
            reader.readAsDataURL(file);
        }
        
        // Check the format of the book and ensure the book file is valid
        const bookFileInput = document.getElementById('bookFile');
        const bookFile = bookFileInput.files[0];
        const format = document.getElementById("format").value;
     
        if (bookFile) {
          if (format === "eBook" && bookFile.type !== "application/epub+zip") {
              alert('Only EPUB files are allowed for eBooks!');
              return;
          } else if (format === "Audio" && !["audio/mp3", "audio/mpeg"].includes(bookFile.type)) {
              alert('Only MP3 files are allowed for Audio books!');
              return;
          }
          const bookreader = new FileReader();
          bookreader.onloadend = function() {
              bookFileValid = true;
          };
          bookreader.readAsDataURL(bookFile);
      }

       submitForm(formData);
    }
}

async function submitForm(formData){
    console.log(formData);
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));
    event.preventDefault();
    fetch('/catalog/modify-item', {
      method: 'POST',
      body: formData
    })
    .then(response => {
        if (response.status === 409) {
            fetchBooks();
            return response.json().then(result => {
              document.getElementById('modal-body').innerHTML = formatModal(true);
              myModal.show();
              console.log(result);
            });
        } else if (response.ok) {
            document.getElementById('modal-body').innerHTML = formatModal(false);
            myModal.show();
            const closeButton = document.querySelector('.btn-close');
            closeButton.addEventListener('click', function () {
              document.getElementById("modifyBookForm").reset();
              window.location.href = "/catalog/modify-item"; 
            });
            
        } else {
            fetchBooks();
            document.getElementById('modal-body').innerHTML = formatModal(true);
            myModal.show();
        }
    })
    .catch(error => console.error('Error:', error));
}

function cancel(){
    fetchBooks();
    //document.getElementById("modifyBookForm").reset();
    populateModifyForm(selectedBook);

    const imagePreview = document.getElementById('imagePreview');
    imagePreview.src = "";
    imagePreview.style.display = 'none';
    const imageUpload = document.getElementById('imageUpload');
    imageUpload.value = '';

    const fileSection = document.getElementById('fileUploadSection');
    const bookFile = document.getElementById('bookFile');
    bookFile.value = '';
  }

function back(){
    document.getElementById("bookDetailsForm").style.display = 'none';
    displayBookDetails(selectedBook);
}

function menuReturn(){
  window.location.href = "/catalog/edit_inventory";
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

document.querySelector("#modifyButton").addEventListener("submit", modifyBook);