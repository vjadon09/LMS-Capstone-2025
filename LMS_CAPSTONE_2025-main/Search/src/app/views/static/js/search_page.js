let selectedBook = null;
let searchResults = []; // Store search results globally
let popularBooks = [];
let newestBooks = [];
let currentIndex = -1;

document.addEventListener("DOMContentLoaded", async function() {
    fetchPopularBooks();
    fetchNewestBooks();
    
    // Add event listener for the search button
    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', handleSearchButtonClick); 

    // Monitor input changes to display suggestions dynamically
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', searchBooks);
    searchInput.addEventListener('keydown', handleSearchEnter);

    try {
        const response = await fetch("/search/review-reservations", {
            method: "GET",
            credentials: "include",
            headers: { "Content-Type": "application/json" }
        });

        const data = await response.json();
        //alert(data.message);
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to update reservations.");
    }
});

// Function to fetch popular books from the backend
async function fetchPopularBooks() {
    try {
        const response = await fetch("/search/popular");
        const data = await response.json();
        console.log(data);
        if (data.isbns) {
            const numBooksSlide = 5;
            const numSlides = 2;
            popularBooks = data.isbns.slice(0, numBooksSlide * numSlides);
            
            // Get cover images
            for (let i = 0; i < popularBooks.length; i++) {
                let isbn = popularBooks[i];
                try {
                    const coverResponse = await fetch(`/search/serve-book-cover/${isbn}`);
                    if (coverResponse.ok) {
                        let blob = await coverResponse.blob();
                        let coverBlob = new Blob([blob], { type: "image/jpg" });
                        let blobUrl = URL.createObjectURL(coverBlob);
                        popularBooks[i] = { isbn, coverUrl: blobUrl };
                    } else {
                        popularBooks[i] = { isbn, coverUrl: "/search/static/images/error.png" };
                    }
                } catch (coverError) {
                    console.error(`Error fetching cover for ISBN: ${isbn}`, coverError);
                    popularBooks[i] = { isbn, coverUrl: "/search/static/images/error.png" };
                }
            }
            displayBooksForCarousel(popularBooks, "popular-inner");
        } else {
            console.error('No popular books found in the response');
        }
    } catch (error) {
        console.error("Error fetching popular books:", error);
    }
}

// Function to fetch newest books from the backend
async function fetchNewestBooks() {
    try {
        const response = await fetch("/search/newest");
        const data = await response.json();
        console.log(data);
        if (data.isbns) {
            const numBooksSlide = 5;
            const numSlides = 2;
            newestBooks = data.isbns.slice(0, numBooksSlide * numSlides);
            // Get cover images
            for (let i = 0; i < newestBooks.length; i++) {
                let isbn = newestBooks[i];
                try {
                    const coverResponse = await fetch(`/search/serve-book-cover/${isbn}`);
                    if (coverResponse.ok) {
                        let blob = await coverResponse.blob();
                        let coverBlob = new Blob([blob], { type: "image/jpg" });
                        let blobUrl = URL.createObjectURL(coverBlob);
                        newestBooks[i] = { isbn, coverUrl: blobUrl };
                    } else {
                        newestBooks[i] = { isbn, coverUrl: "/search/static/images/error.png" };
                    }
                } catch (coverError) {
                    console.error(`Error fetching cover for ISBN: ${isbn}`, coverError);
                    carousnewestBookselBooks[i] = { isbn, coverUrl: "/search/static/images/error.png" };
                }
            }
            displayBooksForCarousel(newestBooks, "newest-inner");
        }
    } catch (error) {
        console.error("Error fetching newest books:", error);
    }
}

// Function to search books dynamically when "Search" input changes
async function searchBooks() {
    const query = document.getElementById('searchInput').value;
    if (query === "") {
        clearSearchResults();
        selectedBook = null;
        const bookList = document.getElementById('bookList');
        bookList.innerHTML = ''; // Clear previous results
    } else {
        try {
            const response = await fetch(`/search/searchQuery?query=${encodeURIComponent(query)}`, {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });

            if (response.ok) {
                const data = await response.json();
                
                // Store the results globally for later use
                if (data.books && data.books.length > 0) {
                    searchResults = data.books;
                    displaySearchResults(searchResults);
                } else {
                    clearSearchResults();
                    const bookList = document.getElementById('bookList');
                    bookList.innerHTML = '<li class="list-group-item">No books found.</li>';
                }
            } else {
                clearSearchResults();
                const bookList = document.getElementById('bookList');
                bookList.innerHTML = `<li class="list-group-item">Nothing matched ${query}.</li>`;
            }
        } catch (error) {
            console.error("Error searching for books:", error);
            clearSearchResults();
            const bookList = document.getElementById('bookList');
            bookList.innerHTML = '<li class="list-group-item">Error fetching books.</li>';
        }
    }
}

// Handle search button click - Redirect to search result page
function handleSearchButtonClick() {
    const query = document.getElementById('searchInput').value;
    
    if (query) {
        // Set the redirect URL dynamically using setAttribute
        const searchUrl = `/search/search_result_page?query=${encodeURIComponent(query)}`;
        window.location.setAttribute('href', searchUrl); // Using setAttribute for setting the location.href
    }
}

// Handle search button click - Redirect to search result page
function handleSearchEnter(event) {
  if (event.key === 'Enter'){
    const query = document.getElementById('searchInput').value;
    if (query) {
      window.location.href = `/search/search_result_page?query=${encodeURIComponent(query)}`
      event.preventDefault();
    }
  }
}

// Function to display books as search results (but not redirect yet)
function displaySearchResults(books) {
    const bookList = document.getElementById('bookList');
    bookList.innerHTML = ''; // Clear previous results

    books.forEach(book => {
        const listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        listItem.textContent = `${book.title} by ${book.author} (${book.format})`;
        listItem.onclick = function() {
          window.location.href = `/search/book_info?isbn=${book.isbn}`;
        };
        
        bookList.appendChild(listItem);
      });
}

// Function to clear the search results
function clearSearchResults() {
    document.getElementById('bookList').innerHTML = '';
}

// Function to display books in a carousel
function displayBooksForCarousel(booksToDisplay, carouselId) {
    const carouselInner = document.getElementById(carouselId);
    const chunkedBooks = chunkBooks(booksToDisplay, 5);
    
    chunkedBooks.forEach((chunk, index) => {
        const carouselSlide = createCarouselSlide(chunk, index);
        carouselInner.appendChild(carouselSlide);
    });
   
}

// Helper function to group books into chunks
function chunkBooks(booksToDisplay, size) {
    const result = [];
    for (let i = 0; i < booksToDisplay.length; i += size) {
        result.push(booksToDisplay.slice(i, i + size));
    }
    return result;
}

// Function to create a carousel item with book images
function createCarouselSlide(bookChunk, index) {
    const carouselItem = document.createElement('div');
    const carouselItemInner = document.createElement('div');
    carouselItemInner.classList.add('row', 'justify-content-center');

    if (index === 0){
        carouselItem.classList.add('carousel-item', 'active');
    }
    else{
        carouselItem.classList.add('carousel-item');
    }   

    id = "carousel-item-" + index + "-image-";
    
    bookChunk.forEach((book, i) =>{   
        
        const bookCard = document.createElement('div');
        bookCard.classList.add('col-2', 'd-flex', 'justify-content-center', 'align-items-center'); 
       
        const aTag = document.createElement('a');
        aTag.href = `/search/book_info?isbn=${book.isbn}`;

        const imgTag = document.createElement('img');
        imgTag.src = book.coverUrl || "/search/static/images/error.png";
        imgTag.classList.add('img-fluid', 'bookCover');
        imgTag.alt = book.title || "Book Cover"; 

        aTag.appendChild(imgTag);
        bookCard.appendChild(aTag);
        carouselItemInner.appendChild(bookCard);        
    });

    carouselItem.append(carouselItemInner);
    return carouselItem;
}

document.getElementById('searchButton').addEventListener('click', function(event) {
    const query = document.getElementById('searchInput').value;
    if (!query) {
        event.preventDefault(); // Stop form submission if the query is empty
        return;
    }
    
    document.getElementById('hiddenSearchInput').value = query; // Set the hidden input value
});