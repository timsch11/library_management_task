// viewer.js

window.onload = function () {
    const params = getQueryParams();
    const type = params['type'];
    const id = params['id'];

    if (type && id) {
        displayEntity(type, id);
    } else {
        document.getElementById('content').innerHTML = '<p>Invalid parameters.</p>';
    }
};

/**
 * Function to retrieve query parameters from the URL.
 * @returns {Object} An object containing key-value pairs of query parameters.
 */
function getQueryParams() {
    const params = {};
    window.location.search.substring(1).split("&").forEach(pair => {
        const [key, value] = pair.split("=");
        if (key) {
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
    });
    return params;
}

/**
 * Fetches a description from the Gemini API for the given entity.
 * @param {string} entityName - The name of the entity (book, author, genre, etc.).
 */
async function fetchGeminiDescription(type, entityName) {
    console.log('Fetching description for:', entityName); // Debug
    try {
        const response = await fetch(`/api/description?type=${type}&name=${encodeURIComponent(entityName)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Fetch response status:', response.status); // Debug

        if (response.status === 400) {
            throw new Error('Invalid request. Entity name is missing.');
        } else if (response.status === 500) {
            throw new Error('Server error while fetching description.');
        } else if (!response.ok) {
            throw new Error('Unexpected error occurred.');
        }

        const data = await response.json();
        console.log('Received data:', data); // Debug
        const descriptionMarkdown = data.description || 'No description available.';

        // Convert Markdown to HTML using Marked.js
        const descriptionHTML = marked.parse(descriptionMarkdown);

        // Display the description in the "description" div
        document.getElementById('description').innerHTML = `<h2>Description</h2>${descriptionHTML}`;
    } catch (error) {
        console.error('Error fetching description from Gemini API:', error);
        document.getElementById('description').innerHTML = `<p>${error.message}</p>`;
    }
}

async function displayEntity(type, id) {
    try {
        // Fetch the main entity data from API
        const response = await fetch(`/api/${type.toLowerCase()}?id=${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${type.toLowerCase()} with ID ${id}`);
        }
        
        const data = await response.json();
        if (!data || data.length === 0) {
            document.getElementById('content').innerHTML = '<p>Entity not found.</p>';
            return;
        }

        const entity = data[0];
        const entityType = type.charAt(0).toUpperCase() + type.slice(1);
        
        // Extract entity name for description
        let entityName = '';
        if (type.toLowerCase() === 'books') {
            entityName = entity.title;
        } else {
            entityName = entity.name;
        }
        
        // Build the HTML content
        let htmlContent = `<h1>${entityType} Details</h1><ul>`;
        
        // Add all properties to the list
        for (const [key, value] of Object.entries(entity)) {
            console.log(key);
            if (key === 'id' || key === "description") continue; // skip id and description
            
            // Handle related entities
            if (key === 'author' && value) {
                // Fetch author details
                const authorResponse = await fetch(`/api/author?id=${value}`);
                if (authorResponse.ok) {
                    const authorData = await authorResponse.json();
                    if (authorData && authorData.length > 0) {
                        htmlContent += `<li><strong>Author:</strong> <a href="viewer.html?type=author&id=${value}">${authorData[0].name}</a></li>`;
                    }
                }
            } else if (key === 'publisher' && value) {
                // Fetch publisher details
                const publisherResponse = await fetch(`/api/publisher?id=${value}`);
                if (publisherResponse.ok) {
                    const publisherData = await publisherResponse.json();
                    if (publisherData && publisherData.length > 0) {
                        htmlContent += `<li><strong>Publisher:</strong> <a href="viewer.html?type=publisher&id=${value}">${publisherData[0].name}</a></li>`;
                    }
                }
            } else if (key === 'genre' && value) {
                // Fetch genre details
                const genreResponse = await fetch(`/api/genre?id=${value}`);
                if (genreResponse.ok) {
                    const genreData = await genreResponse.json();
                    if (genreData && genreData.length > 0) {
                        htmlContent += `<li><strong>Genre:</strong> <a href="viewer.html?type=genre&id=${value}">${genreData[0].name}</a></li>`;
                    }
                }
            } else if (value !== null) {
                // Regular property
                const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ');
                htmlContent += `<li><strong>${formattedKey}:</strong> ${value}</li>`;
            }
        }
        
        htmlContent += '</ul>';
        
        // If viewing a Book, display borrowing details from localStorage (maintaining the original functionality)
        if (type === 'books') {
            const borrowingData = JSON.parse(localStorage.getItem('borrowingData')) || {};
            const borrowingDetails = borrowingData[id];
            
            if (borrowingDetails) {
                htmlContent += `<h2>Borrowing Details</h2><ul>
                    <li><strong>Borrower:</strong> ${borrowingDetails.borrowerName}</li>
                    <li><strong>Borrow Date:</strong> ${borrowingDetails.borrowDate}</li>
                    <li><strong>Return Date:</strong> ${borrowingDetails.returnDate}</li>
                </ul>`;
            } else {
                htmlContent += `<p>This book is currently available for borrowing.</p>`;
            }
        }
        
        // Add a back link to the main catalog
        htmlContent += `<a href="/" class="back-link">&larr; Back to Catalog</a>`;
        
        // Display the content
        document.getElementById('content').innerHTML = htmlContent;
        
        // Fetch and display the Gemini description
        if (entityName) {
            fetchGeminiDescription(type, entityName);
        }
        
    } catch (error) {
        console.error('Error displaying entity:', error);
        document.getElementById('content').innerHTML = `<p>Error loading entity details: ${error.message}</p>`;
    }
}
