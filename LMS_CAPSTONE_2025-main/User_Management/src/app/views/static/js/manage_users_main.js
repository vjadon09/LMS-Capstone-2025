let users = [];

async function fetchUsers() {
  try {
    const response = await fetch("/userManage/all-users");
    if (!response.ok) {
      alert("Error getting all users!");
      return;
    }
    users = await response.json();
    users.forEach((user) => {
      // Convert the 'created_on' field into a readable date
      const createdOnDate = new Date(user.created_on);
      const formattedDate = createdOnDate.toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      user.created_on = formattedDate;
    });
    createTable();  // Call createTable after fetching users
  } catch (error) {
    console.error("Error fetching users:", error);
  }
}

// Create the user table and limit to 10 users
function createTable() {
  const userTable = document.getElementById('user-table');
  userTable.innerHTML = ''; // Clear the table before adding rows

  // Loop through only the first 15 users
  users.forEach(user => {
      const row = document.createElement('tr');
      row.id = `${user.email}`;
      row.innerHTML = `
          <td>${user.name}</td>
          <td>${user.email}</td>
          <td>${user.status}</td>
          <td>${user.created_on}</td>
          <td>
            <a href="/userManage/edit-user/${user.email}/${user.status}">✏️</a>
            <a href="/userManage/delete-user/${user.email}/${user.status}">✖️</a>
          </td>
      `;
      userTable.appendChild(row);
  });
}

// Function to search the users dynamically
function searchUsers() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  if (query === "") {
    resetTable();
  } else {
    const filteredUsers = users.filter(user =>
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    );
    displayUsers(filteredUsers);
  }
}

function displayUsers(usersToDisplay) {
  const userList = document.getElementById('user-list');
  userList.innerHTML = ''; // Clear existing search results
  
  if (usersToDisplay.length === 0) {
    userList.innerHTML = '<li class="list-group-item">No user found.</li>';
  } else {
    usersToDisplay.forEach(user => {
      const listItem = document.createElement('li');
      listItem.classList.add('list-group-item');
  
      const userButton = document.createElement('button');
      userButton.classList.add('btn', 'btn-custom-search', 'w-100', 'p-1');
      userButton.innerHTML = `<p>${user.name} (${user.email})</p>`;
  
      // When clicked, filter the table
      userButton.addEventListener('click', () => {
        filterTable(user);
      });
  
      listItem.appendChild(userButton);
      userList.appendChild(listItem);
    });
  }
}

function filterTable(user) {
  const query = user.email.toLowerCase(); 
  const tableRows = document.querySelectorAll('#user-table tr'); 

  tableRows.forEach(row => {
    const emailCell = row.querySelector('td:nth-child(2)');
    if (emailCell && emailCell.textContent.toLowerCase().includes(query)) {
      row.style.display = 'table-row'; 
    } else {
      row.style.display = 'none'; 
    }
  });
}

function clearSearchResults() {
    const userList = document.getElementById('user-list');
    userList.innerHTML = ''; 
}

function resetTable(){
    const table = document.getElementById('user-table');
    const tableRows = table.querySelectorAll('tr');
    tableRows.forEach(row => {row.style.display = '' });
    document.getElementById('searchForm').reset();
    document.getElementById('user-list').innerHTML = '';
}

function adduser(){
  window.location.href = "/userManage/add-user";
}

document.addEventListener("DOMContentLoaded", function () {
  fetchUsers();
});

document.getElementById('searchForm').addEventListener('submit', (event) => {
  event.preventDefault();
  searchUsers();
});
