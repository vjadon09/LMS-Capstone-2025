// Holds Data
let holdsData = [];

async function loadHolds() {
    try {
        const response = await fetch('/mylib/pending-holds', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({}) 
        });
        if (!response.ok) {
            alert("Failed to fetch hold requests");
            return;
        }

        const holdsData = await response.json();
        const holdsTable = document.getElementById("holdsTable");
        holdsTable.innerHTML = ""; // Reset the table

        holdsData.forEach((hold) => {
            const reservationDate = new Date(hold.reservationDate);
            const formattedDate = reservationDate.toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric'
            });
            let row = `<tr class="book-row"><td>${hold.title}</td><td class="queue-position">${hold.queue}</td><td>${formattedDate}</td></tr>`;
            holdsTable.innerHTML += row;
        });
    } catch (error) {
        console.error("Error loading hold requests:", error);
    }
}

// Checked Out Books Data
let checkedOutData = [];

async function loadCheckedOutBooks() {
    try {
        const response = await fetch('/mylib/completed-holds', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({})
        });
        if (!response.ok) {
            alert("Failed to fetch checked out books");
            return;
        }

        checkedOutData = await response.json();
        const checkedOutTable = document.getElementById("checkedOutTable");
        checkedOutTable.innerHTML = ""; //reset the table

        checkedOutData.forEach((book) => {
            const expirationDate = new Date(book.expirationDate);
            const formattedDate = expirationDate.toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric'
            });
            let row = `
                <tr class="book-row">
                    <td>${book.title}, (${book.format})</td>
                    <td>${book.daysLeft} days</td>
                    <td>${formattedDate}</td>
                    <td><a href="/mylib/access/${book.isbn}">Access</a></td>
                </tr>`;
            checkedOutTable.innerHTML += row;
        });
    } catch (error) {
        console.error("Error loading checked out books:", error);
    }
}

let selectedWishlistItems = new Set();
let wishlistData = [];

// Wishlist
async function loadWishlist() {
    try {
        // Send a POST request to fetch the wishlist from the FastAPI backend
        const response = await fetch('/mylib/wishlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
        });

        if (!response.ok) {
            alert("Failed to load wishlist");
            return;
        }

        wishlistData = await response.json(); 
        const wishlist = document.getElementById("wishlist");
        wishlist.innerHTML = "";

        if (wishlistData.length === 0) {
            wishlist.innerHTML = `
                 <p class="empty-wishlist-message">
                    <span>📚</span> Your wishlist is empty! Add some books to get started. <span>✨</span>
                </p>
            `;
        } else {
            // Iterate over the wishlist items and add them to the list
            wishlistData.forEach((book) => {
            let listItem = document.createElement("li");
            listItem.classList.add("list-group-item", "wishlist-item");
            listItem.innerHTML = `<b>${book.title}</b>&nbsp;&nbsp;|&nbsp;&nbsp;<i>${book.isbn}</i>`;

            // Toggle selection on click
            listItem.addEventListener("click", function () {
                if (selectedWishlistItems.has(book.isbn)) {
                    selectedWishlistItems.delete(book.isbn);
                    listItem.classList.remove("wishlist-item-active", "selected");
                } else {
                    selectedWishlistItems.add(book.isbn);
                    listItem.classList.add("wishlist-item-active", "selected");
                }
            });

            wishlist.appendChild(listItem);
        });
        }
    } catch (error) {
        console.error("Error loading wishlist:", error);
    }
}


// Add to Wishlist
function addToWishlist() {
    window.location = '/mylib/search';
}

// Remove from Wishlist
async function removeFromWishlist() {
    if (selectedWishlistItems.size === 0) {
        alert("No items selected to remove.");
        return;
    }

    const items = encodeURIComponent(Array.from(selectedWishlistItems).join(","));
    await fetch(`/mylib/wishlist/remove/${items}`, {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location = "/mylib/dashboard";
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error removing books from your wishlist.');
    });
}

// Clear Wishlist
function clearWishlist() {
    fetch('/mylib/wishlist/clear', {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location = "/mylib/dashboard";
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error clearing the wishlist.');
    });
}

// Filter Books by Name
function filterBooks() {
    let filter = document.getElementById("bookFilter").value.toLowerCase();
    let bookRows = document.querySelectorAll(".book-row");

    bookRows.forEach(row => {
        let bookTitle = row.cells[0].textContent.toLowerCase();
        row.style.display = bookTitle.includes(filter) ? "" : "none";
    });
}

let asc = true;

function sortByDueDate() {
    asc = !asc;
    checkedOutData.sort((a, b) => {
        return asc ? a.daysLeft - b.daysLeft : b.daysLeft - a.daysLeft;
    });
    const sortButton = document.querySelector("button.btn.btn-dark");
    sortButton.textContent = asc ? "Sort by Due Date 🔼" : "Sort by Due Date 🔽";
    
    // Update table
    const checkedOutTable = document.getElementById("checkedOutTable");
    checkedOutTable.innerHTML = ""; // Clear existing rows

    checkedOutData.forEach((book) => {
        const expirationDate = new Date(book.expirationDate);
        const formattedDate = expirationDate.toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
        });

        let row = `
            <tr class="book-row">
                <td>${book.title}, (${book.format})</td>
                <td>${book.daysLeft} days</td>
                <td>${formattedDate}</td>
                <td><a href="/mylib/access/${book.isbn}">Access</a></td></tr>
        `;
        checkedOutTable.innerHTML += row;
    });
}

window.onload = function() {
    loadHolds();
    loadCheckedOutBooks();
    loadWishlist();
};