/* Things that need to be changed
-read from db
-can change alert messages to something else when hold status is changed
-refresh table after each time one of the buttons are selected
-assign each book a copy number
 */
let books = [];

async function fetchHolds() {
  try {
    const response = await fetch("/reservations/list-holds/");
    if (response.ok) {
      const booksData = await response.json();
      books = [...booksData];
      console.log(books);

      // Update books status
      for (const book of books) {
        const isbn = book.isbn; // Assuming isbn is a field in the hold object
        const book_id = book.book_id; // Assuming book_id is a field in the hold object

        // Call the update_status endpoint for each book/hold
        const updateResponse = await fetch(`/reservations/update-status/${isbn}/${book_id}`);
        const updateData = await updateResponse.json();
        console.log(updateData.message);
      }
      // Create the UI
      createTable(books);
    } else {
      console.error("Failed to fetch reservations:", response.status);
    }
  } catch (error) {
    console.error("Error fetching reservations:", error);
  }
}

async function fetchBooksISBN(isbn) {
    try {
        const response = await fetch(`/reservations/book-title/${isbn}`);

        if (response.ok) {
            const data = await response.json();
            return data.title;
        } else {
            console.error("Failed to fetch book title:", response.status);
            return null;
        }
    } catch (error) {
        console.error("Error fetching book title:", error);
        return null;
    }
}  

function formatDate(dateString) {
    if (!dateString) return "ERR"; // Handle missing dates
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { 
        year: "numeric", 
        month: "short", 
        day: "numeric" 
    });
}

async function createTable(filteredBooks = books) {
    let i = 1;
    const table = document.getElementById('book-table');
    table.innerHTML = '';

    for (const book of filteredBooks) {
        let title = book.title;
        if (!title) {
            title = await fetchBooksISBN(book.isbn) || "Unknown Title";
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="checkbox" class="selectRow"></td>
            <th scope="row">${i}</th>
            <td>${title}</td>
            <td>${book.isbn}</td>
            <td>${book.book_id}</td>
            <td>${book.user_email}</td>
            <td>${formatDate(book.reservation_date)}</td>
            <td>${formatDate(book.expiration_date)}</td>
            <td>${book.status}</td>
        `;
        table.appendChild(row);
        i++;
    }
}

window.onload = async () => {
    await fetchHolds();
}

// -------------------------------- Helper Functions --------------------------------

$(document).ready(function() {
    // Select or deselect a single row checkbox
    $(".selectRow").click(function() {
      var row = $(this).closest("tr");
  
      // Uncheck all other checkboxes and remove 'selected' class from other rows
      $(".selectRow").not(this).prop("checked", false).closest("tr").removeClass("selected");
  
      // If the clicked row checkbox is checked, highlight the row
      if ($(this).prop("checked")) {
        row.addClass("selected");
      } else {
        row.removeClass("selected");
      }
    });
});

// Get all the filter checkboxes
const filterCheckboxes = document.querySelectorAll('.form-check-input');
const searchInput = document.getElementById('searchInput');
let filterOpt = '';

// Function to ensure only one filter is selected at a time
function restrictSingleFilterSelection() {
  filterCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener('change', function() {
      if (this.checked) {
        // Update the filterOpt when a checkbox is selected
        filterOpt = this.value;

        // Uncheck other checkboxes
        filterCheckboxes.forEach((otherCheckbox) => {
          if (otherCheckbox !== this) {
            otherCheckbox.checked = false; 
          }
        });
      } else {
        if (!isAnyFilterSelected()) {
          filterOpt = ''; 
          console.log('No filter selected');
        }
      }
      toggleSearchInput(); 
    });
  });
}

// Function to check if any filter is selected
function isAnyFilterSelected() {
  let isSelected = false;
  filterCheckboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      isSelected = true;
    }
  });
  return isSelected;
}

// Function to enable or disable the search input based on filter selection
function toggleSearchInput() {
  if (isAnyFilterSelected()) {
    searchInput.disabled = false;
  } else {
    searchInput.disabled = true;
  }
}

// Initialize the filter restriction and enable/disable search input
restrictSingleFilterSelection();
toggleSearchInput();


filterCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener('change', toggleSearchInput); 
});

toggleSearchInput(); 
restrictSingleFilterSelection();

// Function to search the books dynamically
function searchBooks() {
    const query = searchInput.value.toLowerCase();
    let filteredBooks = [...books];
    console.log(filteredBooks);
    if (query === "") {
        createTable(filteredBooks);
        return;
    }

    if (filterOpt === 'isbn') {
        filteredBooks = books.filter(book => book.isbn.toLowerCase().includes(query));
    }
    else if (filterOpt === 'bookID') {
        filteredBooks = books.filter(book => book.book_id.toLowerCase().includes(query));
    }
    else if (filterOpt === 'user') {
        filteredBooks = books.filter(book => book.user_email.toLowerCase().includes(query));
    }
    else if (filterOpt === 'holdDate') {
        filteredBooks = books.filter(book => formatDate(book.reservation_date).toLowerCase().includes(query));
    }
    else if (filterOpt === 'dueDate') {
        filteredBooks = books.filter(book => formatDate(book.expiration_date).toLowerCase().includes(query));
    }
    createTable(filteredBooks);
}
  
  // Function to display the list of books based on isbn
  function displayTitle(titlesToDisplay) {
    const searchList = document.getElementById('bookList');
    searchList.innerHTML = ''; // Clear the existing list
    if (titlesToDisplay.length === 0) {
        searchList.innerHTML = '<li class="list-group-item">No entries found.</li>';
    } else {
        titlesToDisplay.forEach(title => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            
            // Create a button for each book
            const itemButton = document.createElement('button');
            itemButton.classList.add('btn', 'btn-custom-search', 'w-100');
            itemButton.innerHTML = `<p align="left">${title}</p>`;
            
            itemButton.addEventListener('click', () => {
                filterTable(title, 'title');  
                clearSearchResults(); 
            });
            listItem.appendChild(itemButton);
            searchList.appendChild(listItem);
        });
    }
  }
  
  // Function to display the list of books based on title
  function displayIsbn(isbnToDisplay) {
    const searchList = document.getElementById('bookList');
    searchList.innerHTML = ''; // Clear the existing list
    if (isbnToDisplay.length === 0) {
        searchList.innerHTML = '<li class="list-group-item">No entries found.</li>';
    } else {
        isbnToDisplay.forEach(isbn => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            
            // Create a button for each book
            const itemButton = document.createElement('button');
            itemButton.classList.add('btn', 'btn-custom-search', 'w-100');
            itemButton.innerHTML = `<p align="left">${isbn}</p>`;
            
            itemButton.addEventListener('click', () => {
                filterTable(isbn, 'isbn');  
                clearSearchResults(); 
            });
            listItem.appendChild(itemButton);
            searchList.appendChild(listItem);
        });
    }
  }

// Function to display the list of books based on user
function displayUser(usersToDisplay) {
    const searchList = document.getElementById('bookList');
    searchList.innerHTML = ''; // Clear the existing list
    if (usersToDisplay.length === 0) {
        searchList.innerHTML = '<li class="list-group-item">No entries found.</li>';
    } else {
        usersToDisplay.forEach(user => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            
            // Create a button for each book
            const itemButton = document.createElement('button');
            itemButton.classList.add('btn', 'btn-custom-search', 'w-100');
            itemButton.innerHTML = `<p align="left">${user}</p>`;
            
            itemButton.addEventListener('click', () => {
                filterTable(user, 'user');  
                clearSearchResults(); 
            });
            listItem.appendChild(itemButton);
            searchList.appendChild(listItem);
        });
    }
} 

function filterTableByDate(dateToDisplay, dateType) {
    const searchList = document.getElementById('bookList');
    searchList.innerHTML = ''; // Clear the existing list
    if (dateToDisplay.length === 0) {
        searchList.innerHTML = '<li class="list-group-item">No entries found.</li>';
    } else {
        dateToDisplay.forEach(date => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            
            // Create a button for each book
            const itemButton = document.createElement('button');
            itemButton.classList.add('btn', 'btn-custom-search', 'w-100');
            itemButton.innerHTML = `<p align="left">${date}</p>`;
            
            itemButton.addEventListener('click', () => {
                filterTable(date, dateType);  
                clearSearchResults(); 
            });
            listItem.appendChild(itemButton);
            searchList.appendChild(listItem);
        });
    }
}

function resetTable() {
    document.getElementById("searchInput").value = "";
    document.querySelectorAll('.form-check-input').forEach(checkbox => {
        checkbox.checked = false;
    });
    document.getElementById("searchInput").disabled = true;
    filterOpt = '';
    createTable(books);
}

function clearSearchResults() {
    const bookList = document.getElementById('bookList');
    bookList.innerHTML = ''; 
}

const table = document.getElementById('book-table');
const tableRows = table.querySelectorAll('tr');

function filterTable(book, filter){
    const query = book.toLowerCase();
    let filteredBooks = [...books];

    filteredBooks = filteredBooks.filter(row => {
        const cells = row.querySelectorAll('td');
        if (filter === 'user') {
            return cells[4].textContent.toLowerCase().includes(query);
        } else if (filter === 'isbn') {
            return cells[2].textContent.toLowerCase().includes(query);
        } else if (filter === 'title') {
            return cells[1].textContent.toLowerCase().includes(query);
        } else if (filter === 'holdDate') {
            return cells[5].textContent.toLowerCase().includes(query);
        } else if (filter === 'dueDate') {
            return cells[6].textContent.toLowerCase().includes(query);
        }
    });

    //createTable(filteredBooks);
}

// Function to get the checked row
function getCheckedRow() {
    const checkedCheckbox = document.querySelector('.selectRow:checked'); 
    if (checkedCheckbox) {
      const row = checkedCheckbox.closest('tr'); 
      return row; 
    }
    return null; 
  }

async function cancelHold() {
    const checkedRow = getCheckedRow();
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));
  
    if (!checkedRow) {
      document.getElementById('modal-body').innerHTML = formatModal(true, "Select a row.");
      myModal.show();
      return;
    }
    const isbn = checkedRow.querySelector('td:nth-child(4)').textContent;
    const book_id = checkedRow.querySelector('td:nth-child(5)').textContent;

    try {
        const response = await fetch(`/reservations/delete-hold/${isbn}/${book_id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            document.getElementById('modal-body').innerHTML = formatModal(false, "Successfully deleted hold!");
            myModal.show();
            const closeButton = document.querySelector('.btn-close');
            await fetchHolds();
            closeButton.addEventListener('click', function () {
              window.location.reload();
            });
        } else {
            document.getElementById('modal-body').innerHTML = formatModal(true, "Failed to delete hold.");
            myModal.show();
        }
    } catch (error) {
        console.error("Error deleting hold:", error);
        document.getElementById('modal-body').innerHTML = formatModal(false, "An error occurred while deleting the hold.");
        myModal.show();
    }
}

async function extendHold() {
    const checkedRow = getCheckedRow();
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));

    if (!checkedRow) {
      document.getElementById('modal-body').innerHTML = formatModal(true, "Select a row.");
      myModal.show();
      return;
    }
    const isbn = checkedRow.querySelector('td:nth-child(4)').textContent;
    const book_id = checkedRow.querySelector('td:nth-child(5)').textContent;
    
    try {
        const response = await fetch(`/reservations/extend-hold/${isbn}/${book_id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            document.getElementById('modal-body').innerHTML = formatModal(false, "Successfully extended hold!");
            myModal.show();
            const closeButton = document.querySelector('.btn-close');
            await fetchHolds();
            closeButton.addEventListener('click', function () {
              window.location.reload();
            });
        } else {
            document.getElementById('modal-body').innerHTML = formatModal(true, "Failed to extend hold.");
            myModal.show();
        }
    } catch (error) {
        console.error("Error extending hold:", error);
        document.getElementById('modal-body').innerHTML = formatModal(true, "An error occurred while extending the hold.");
        myModal.show();
    }
}

function goBack(){
    window.location = '/reservations/dashboard';
}

function formatModal(error, message){
  let modalBody;
  if (error){
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">❎</p></div>
                <div class="row"><p class="text-center fs-5">${message}</p></div>
                <div class="row"><p class="text-center">Please try again.</p></div>`
    
  } else{
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">✅</p></div>
                <div class="row"><p class="text-center fs-5">${message}!</p></div>`
  }
  return modalBody
}

// Dynamically filter books
let searchTimeout;

searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        searchBooks();
    }, 1000);
});