let starRating;

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const isbn = urlParams.get("isbn") || ""; // Default to empty string if no isbn is provided
    
    displayStarFields();
    // Fetch book data based on the query (initial load)
    fetchBooks(isbn);

    fetchReviews(isbn);

    // Set up wishlist button
    let wishButton = document.getElementById('wishlist-button');
    wishButton.addEventListener('click', function() {
        addToWishlist(isbn);
    });

    // Set up wishlist button
    let placeHoldButton = document.getElementById("hold-button");
    placeHoldButton.addEventListener('click', function() {
        placeHold(isbn);
    });
    
    let reviewButton = document.getElementById("review-button");
    if (reviewButton) {
        reviewButton.addEventListener("click", function(event) {
            event.preventDefault();
            submitReview();
        });
    }
    getStarRating();
    
});

async function fetchBooks(isbn) {
    try {
        const response = await fetch(`/search/book_info/${isbn}`);
        if (!response.ok) {
            throw new Error('Failed to fetch book data');
        }
        const itemData = await response.json();

        try {
            const coverResponse = await fetch(`/search/serve-book-cover/${isbn}`);
            if (coverResponse.ok) {
                let blob = await coverResponse.blob();
                let coverBlob = new Blob([blob], { type: "image/jpg" });
                let blobUrl = URL.createObjectURL(coverBlob);
                itemData.coverImage = blobUrl;
            } else {
                itemData.coverImage = "/search/static/images/error.png";
            }
        } catch (coverError) {
            console.error(`Error fetching cover for ISBN: ${isbn}`, coverError);
            itemData.coverImage = "/search/static/images/error.png";
        }
        
        displayBookInfo(itemData);
        
        // Fetch reviews
        fetchReviews(isbn);
    } catch (error) {
        console.error('Error fetching book info:', error);
    }
}

function displayBookInfo(itemData) {
    const title = document.getElementById("book-title");
    const bookStatus = document.getElementById("status");
    if (itemData.format === "eBook"){ 
      title.textContent = '📖' + itemData.title;
    }
    else {
      title.textContent = '🎧 ' + itemData.title;
    }
    document.getElementById("book-cover").innerHTML = `<img src="${itemData.coverImage}" class="book-cover img-fluid" alt="Book Cover">`;

    document.getElementById("main-book-info").innerHTML = `
        <h6 class="card-title">Author: ${itemData.author}</h6>
        <p class="card-text">Rating: ${itemData.rating}</p>
        <p class="card-text">Total Copies: ${itemData.numCopies}</p>
        <p class="card-text">${itemData.description}</p>`;

    let bookDetails = `
        <div class="row w-100">   
        <div class="col-6">
        <p class="card-text">ISBN: ${itemData.isbn}</p>
        <p class="card-text">Format: ${itemData.format}</p>
        <p class="card-text">Genre: ${itemData.genre}</p>
        </div>
        <div class="col-6">`;

    if (itemData.format === "eBook") {
        bookDetails += `<p class="card-text">Page Length: ${itemData.pageNumber}</p>`;
    }
    if (itemData.format === "Audio") {
        bookDetails += `<p class="card-text">Hours (Approx): ${getHours(itemData.numOfMins)}</p>`;
    }
    bookDetails += `
        <p class="card-text">Publisher: ${itemData.publisher}</p>`;

    document.getElementById("book-info").innerHTML = bookDetails;
    bookStatus.textContent = itemData.status;
    bookStatus.style.color = 'green';

    const holdButton = document.getElementById('hold-button');
    let wishButton = document.getElementById('wishlist-button');
    holdButton.disabled = false;
    wishButton.disabled = false;

    if(itemData.status === "Not Available"){
        holdButton.disabled = true;
        bookStatus.style.color = 'red';
    }
}

async function fetchReviews(isbn) {
    try {
        // Pass the ISBN as a query parameter in the URL
        const response = await fetch(`/search/retrieve-reviews?isbn=${isbn}`, {
            method: "GET",
            headers: {"Content-Type": "application/json"}
        });

        if (!response.ok) {
            throw new Error('Failed to fetch reviews');
        }

        const reviewData = await response.json();
        displayReviews(reviewData.reviews);
    } catch (error) {
        console.error('Error fetching reviews:', error);
    }
}


function displayReviews(reviews) {
    const commentsList = document.getElementById('commentsList');
    commentsList.innerHTML = ''; // Clear any existing reviews
    reviews.forEach(review => {
        const card = document.createElement('div');
        const dateString = review.created_at;
        const date = new Date(dateString);
        // Options for formatting
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const formattedDate = date.toLocaleDateString('en-US', options);

        card.innerHTML = `
            <div class="card mt-3 mb-3">
                <div class="card-body">
                    <h5 class="card-title d-inline me-2">${review.firstName} ${review.lastName}</h5>
                    <p class="card-text d-inline">${getStars(review.rating)} </p>
                    <div class="d-flex">
                      <p class="card-title details fs-6 fst-italic d-inline me-2">@${review.user}</p>
                      <p class="card-title details d-inline">(${formattedDate})</p>
                    </div>
                    <p class="card-text">${review.review_text}</p> 
                </div>
            </div>`;
        commentsList.appendChild(card);
    });
}

// Get number of stars for review
function getStars(rating) {
    let stars = '';
    for (let i = 1; i <= rating; i++) {
        stars += '⭐';
    }
    return stars;
}

function getHours(minutes){
  let hours = Math.ceil(minutes/60);
  return hours
}

function addToWishlist(isbn) {
    fetch(`/search/add-to-wishlist`, {
        method: "POST",
        credentials: "include",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ isbn: isbn })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.message === "Book successfully added to wishlist!") {
            window.location.href = "/search/mylib";
        }
    })
    .catch(error => {
        console.error("Error adding to wishlist:", error);
    });
}

async function submitReview() {
    const isbn = document.querySelector('input[name="isbn"]').value;
    //const rating = document.getElementById("status").value;
    const rating = starRating;
    const reviewComment = document.getElementById("description").value;
    const reviewButton = document.getElementById("review-button");
    console.log(rating);
    if (!rating || !reviewComment.trim()) {
        alert("Please select a rating and enter a comment.");
        return;
    }
    reviewButton.disabled = true;

    try {
        const response = await fetch("/search/write-review", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                isbn: isbn,
                rating: rating,
                review_comment: reviewComment,
            }),
        });

        if (!response.ok) {
            alert("Failed to submit review");
            return;
        }

        alert("Review submitted successfully!");
        document.getElementById("status").value = "";
        document.getElementById("description").value = "";
        const stars = document.querySelectorAll('.stars i');
        stars.forEach(star => star.classList.remove('active'));
        starRating = null;
        fetchReviews(isbn);

    } catch (error) {
        console.error("Error submitting review:", error);
        alert("Error submitting review. Please try again.");
    } finally {
        reviewButton.disabled = false;
    }
}

async function placeHold(isbn) {
    try {
        const response = await fetch(`/search/place_hold/${isbn}`, {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json" }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            window.location.href = '/search/mylib';
        } else {
            alert(`${data.message || "Unknown error"}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
}

function displayStarFields(){
  const stars = document.querySelectorAll(".stars i");
  // Loop through the "stars" NodeList
  stars.forEach((star, index1) => {
    // Add an event listener that runs a function when the "click" event is triggered
    star.addEventListener("click", () => {
      // Loop through the "stars" NodeList Again
      stars.forEach((star, index2) => {
        // Add the "active" class to the clicked star and any stars with a lower index
        // and remove the "active" class from any stars with a higher index
        index1 >= index2 ? star.classList.add("active") : star.classList.remove("active");
      });
    });
  });
}

function getStarRating(){
  // Get all the star icons
  const stars = document.querySelectorAll('.stars i');
  let rating = 0;
  // Add event listeners to each star
  stars.forEach(star => {
      star.addEventListener('click', function() {
      starRating = this.getAttribute('value');
      console.log(rating);
      });
  });
}