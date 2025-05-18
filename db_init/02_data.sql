-- Insert Genres
INSERT INTO Genre (name, description) VALUES
('Science Fiction', ''),
('Fantasy', 'Stories involving magical elements and fantastical worlds'),
('Non-fiction', '');

-- Insert Publishers
INSERT INTO Publisher (name, description) VALUES
('Orbit Books', ''),
('Penguin Random House', ''),
('HarperCollins', 'A major publisher of fiction and non-fiction books.');

-- Insert Authors
INSERT INTO Author (name, description) VALUES
('Isaac Asimov', ''),
('J.K. Rowling', ''),
('Malcolm Gladwell', 'Canadian journalist and author of non-fiction books.');

-- Insert Borrowers
INSERT INTO Borrower (name) VALUES
('Alice Johnson'),
('Bob Smith'),
('Charlie Nguyen');

-- Insert Books
INSERT INTO Books (id, title, description, present, borrower, author, publisher, genre) VALUES
(1, 'Foundation', '', FALSE, 'Alice Johnson', 1, 1, 1),
(2, 'Harry Potter and the Sorcerer`s Stone', '', TRUE, NULL, 2, 1, 2),
(3, 'Outliers', '', TRUE, NULL, 3, 2, 3),
(4, 'The Hobbit', '', FALSE, 'Bob Smith', 2, 3, 2);
