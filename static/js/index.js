window.onload = function () {
    // Fetch all required data using Promise.all for parallel requests
    Promise.all([
        fetch('/api/books').then(response => response.json()),
        fetch('/api/author').then(response => response.json()),
        fetch('/api/publisher').then(response => response.json()),
        fetch('/api/genre').then(response => response.json()),
        fetch('/api/borrower').then(response => response.json())
    ])
    .then(([books, authors, publishers, genres, borrowers]) => {
        console.log("Books data:", books);
        
        // Convert arrays to lookup objects
        const authorsMap = {};
        const publishersMap = {};
        const genresMap = {};
        
        // Process authors data
        authors.forEach(author => {
            authorsMap[author.id] = author.name;
        });
        
        // Process publishers data
        publishers.forEach(publisher => {
            publishersMap[publisher.id] = publisher.name;
        });
        
        // Process genres data
        genres.forEach(genre => {
            genresMap[genre.id] = genre.name;
        });
        
        // Setup book table and dropdowns
        const bookTable = document.getElementById('book-table');
        const borrowBookSelect = document.getElementById('borrowBookId');
        const returnBookSelect = document.getElementById('returnBookId');
        
        // Retrieve borrowing data from LocalStorage
        // const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};

        
        // Clear existing options
        borrowBookSelect.innerHTML = '<option value="">Select a Book</option>';
        returnBookSelect.innerHTML = '<option value="">Select a Book</option>';

        // Populate book table and dropdowns
        books.forEach(book => {
            const id = book.id;
            const title = book.title;
            const authorId = book.author;
            const publisherId = book.publisher;
            const genreId = book.genre;
            const borrowerName = book.borrower;
            
            const authorName = authorsMap[authorId] || 'Unknown';
            const publisherName = publishersMap[publisherId] || 'Unknown';
            const genreName = genresMap[genreId] || 'Unknown';
            
            // Create table row for each book
            const row = document.createElement('tr');
            row.setAttribute('data-id', id);
            
            // Check if book is borrowed
            const isBorrowed = borrowerName ? true : false;

            console.log(book.borrowdate);
            
            // Populate row with book details
            row.innerHTML = `<td>${id}</td>
                             <td><a href="viewer.html?type=book&id=${id}" target="_blank">${title}</a></td>
                             <td><a href="viewer.html?type=author&id=${authorId}" target="_blank">${authorName}</a></td>
                             <td><a href="viewer.html?type=publisher&id=${publisherId}" target="_blank">${publisherName}</a></td>
                             <td><a href="viewer.html?type=genre&id=${genreId}" target="_blank">${genreName}</a></td>
                             <td>${isBorrowed ? borrowerName : ''}</td>
                             <td>${isBorrowed ? book.borrowdate : ''}</td>
                             <td>${isBorrowed ? book.returndate : ''}</td>
                             <td>${isBorrowed ? 'Borrowed' : 'Present'}</td>`;
            bookTable.appendChild(row);
            
            // Populate the appropriate dropdown
            if (!isBorrowed) {
                // Add book to Borrow dropdown
                const option = document.createElement('option');
                option.value = id;
                option.textContent = `${id} - ${title}`;
                borrowBookSelect.appendChild(option);
            } else {
                // Add book to Return dropdown
                const returnOption = document.createElement('option');
                returnOption.value = id;
                returnOption.textContent = `${id} - ${title}`;
                returnBookSelect.appendChild(returnOption);
            }
        });
    })
    .catch(error => {
        console.error("Error fetching data:", error);
        alert("There was an error loading the library data. Please try refreshing the page.");
    });
};

// Handle Borrow Form Submission
document.getElementById('borrowForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('borrowBookId').value;
    const borrowerName = document.getElementById('borrowerName').value.trim();
    const borrowDate = document.getElementById('borrowDate').value;

    if (!bookId || !borrowerName || !borrowDate) {
        alert('Please fill in all fields.');
        return;
    }

    // Confirmation Dialog
    if (!confirm(`Are you sure you want to borrow Book ID ${bookId}?`)) {
        return;
    }

    const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
    if (row) {
        const currentState = row.cells[8].textContent;
        if (currentState === 'Borrowed') {
            alert('This book is already borrowed.');
            return;
        }

        const returnDate = new Date(borrowDate);
        returnDate.setMonth(returnDate.getMonth() + 3); // Set the return date 3 months later

        // Update the table
        row.cells[5].textContent = borrowerName;
        row.cells[6].textContent = borrowDate;
        row.cells[7].textContent = returnDate.toISOString().split('T')[0]; // Format the date as YYYY-MM-DD
        row.cells[8].textContent = 'Borrowed';
        row.classList.add('borrowed');

        // Save borrowing details to LocalStorage
        /*const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
        borrowingData[bookId] = {
            borrowerName: borrowerName,
            borrowDate: borrowDate,
            returnDate: returnDate.toISOString().split('T')[0]
        };
        localStorage.setItem('borrowingData', JSON.stringify(borrowingData));*/

        console.log(borrowDate)
        console.log(returnDate)

        // Format the returnDate as YYYY-MM-DD before sending
        const formattedReturnDate = returnDate.toISOString().split('T')[0];

        fetch("/api/borrow", {
            method: "POST",
            body: JSON.stringify({
              bookid: bookId,
              name: borrowerName,
              borrowDate: borrowDate,
              returnDate: formattedReturnDate
            }),
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          })
          .then(response => {
            if (!response.ok) {
              return response.json().then(err => {
                throw new Error(err.error || 'Failed to borrow book');
              });
            }
            return response.json();
          })
          .then(data => {
            console.log('Book borrowed successfully:', data);
          })
          .catch(error => {
            console.error('Error borrowing book:', error);
            alert(`Error borrowing book: ${error.message}`);
          });

        // Remove the borrowed book from Borrow Form dropdown
        const borrowBookSelect = document.getElementById('borrowBookId');
        const optionToRemove = borrowBookSelect.querySelector(`option[value="${bookId}"]`);
        if (optionToRemove) {
            optionToRemove.remove();
        }

        // Add the borrowed book to Return Form dropdown
        const returnBookSelect = document.getElementById('returnBookId');
        const newReturnOption = document.createElement('option');
        newReturnOption.value = bookId;
        newReturnOption.textContent = `${bookId} - ${row.cells[1].textContent}`;
        returnBookSelect.appendChild(newReturnOption);

        // Clear the form
        document.getElementById('borrowForm').reset();

        alert(`Book ID ${bookId} has been successfully borrowed.`);
    } else {
        alert('No book found with that ID.');
    }
});

// Handle Return Form Submission
document.getElementById('returnForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const bookId = document.getElementById('returnBookId').value;
    const returnDateInput = document.getElementById('returnDate').value;

    if (!bookId || !returnDateInput) {
        alert('Please fill in all fields.');
        return;
    }

    // Confirmation Dialog
    if (!confirm(`Are you sure you want to return Book ID ${bookId}?`)) {
        return;
    }

    const row = document.querySelector(`#book-table tr[data-id="${bookId}"]`);
    if (row) {
        const currentState = row.cells[8].textContent;
        if (currentState !== 'Borrowed') {
            alert('This book is not currently borrowed.');
            return;
        }

        // Update the table to clear borrowing details
        row.cells[5].textContent = '';
        row.cells[6].textContent = '';
        row.cells[7].textContent = '';
        row.cells[8].textContent = 'Present';
        row.classList.remove('borrowed');

        // Update LocalStorage
        /*const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
        if (borrowingData[bookId]) {
            delete borrowingData[bookId];
            localStorage.setItem('borrowingData', JSON.stringify(borrowingData));
        }*/
        fetch("/api/return", {
            method: "POST",
            body: JSON.stringify({
                bookid: bookId
              }),
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
        });

        // Remove the returned book from Return Form dropdown
        const returnBookSelect = document.getElementById('returnBookId');
        const optionToRemove = returnBookSelect.querySelector(`option[value="${bookId}"]`);
        if (optionToRemove) {
            optionToRemove.remove();
        }

        // Add the returned book back to Borrow Form dropdown
        const borrowBookSelect = document.getElementById('borrowBookId');
        const newBorrowOption = document.createElement('option');
        newBorrowOption.value = bookId;
        newBorrowOption.textContent = `${bookId} - ${row.cells[1].textContent}`;
        borrowBookSelect.appendChild(newBorrowOption);

        // Clear the form
        document.getElementById('returnForm').reset();

        alert(`Book ID ${bookId} has been successfully returned.`);
    } else {
        alert('No book found with that ID.');
    }
});

// Clear borrowing data from localStorage
document.getElementById('clearDataBtn').addEventListener('click', function () {
    if (confirm('Are you sure you want to clear all borrowing data? This action cannot be undone.')) {
        //localStorage.removeItem('borrowingData'); // Only remove borrowing data
        fetch("/api/removeBorrowers", {
            method: "POST",
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          });
        location.reload(); // Reload the page after clearing the data
    }
});

// Book search functionality
document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
    
    if (!searchTerm) {
        // If search is empty, show all books
        showAllBooks();
        return;
    }
    
    // Get all book rows
    const bookRows = document.querySelectorAll('#book-table tr[data-id]');
    
    // Filter books based on search term (title is in the second column)
    bookRows.forEach(row => {
        const title = row.cells[1].textContent.toLowerCase();
        if (title.includes(searchTerm)) {
            row.style.display = ''; // Show the row
        } else {
            row.style.display = 'none'; // Hide the row
        }
    });
});

// Clear search and show all books
document.getElementById('clearSearch').addEventListener('click', function() {
    document.getElementById('searchInput').value = '';
    showAllBooks();
});

// Function to show all books
function showAllBooks() {
    const bookRows = document.querySelectorAll('#book-table tr[data-id]');
    bookRows.forEach(row => {
        row.style.display = ''; // Show all rows
    });
}