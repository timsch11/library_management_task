Borrow:
- use IDs (like a unique username) to identify borrowers to avoid duplicate names and make it easier to add user accounts for borrowers
- store borrow data in seperate table to make it possible to have more than one book of each kind more easily
Book:
- only model title and book description as attribute types (unique to each book)
- model Author, Publisher and Genre as entity types because they exist independantly of the book
Attribute type description:
- avoid generating the same description multiple times by storing the description for each entity -> cheaper
