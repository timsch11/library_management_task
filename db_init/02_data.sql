-- Insert Genres
INSERT INTO Genre (name, description) VALUES
('Science Fiction', 'Fictional stories based on scientific or technological advances'),
('Fantasy', 'Stories involving magical elements and fantastical worlds'),
('Non-fiction', 'Factual works about real events or people');

-- Insert Publishers
INSERT INTO Publisher (name, description) VALUES
('Orbit Books', 'A publisher specializing in science fiction and fantasy.'),
('Penguin Random House', 'One of the largest publishing companies in the world.'),
('HarperCollins', 'A major publisher of fiction and non-fiction books.');

-- Insert Authors
INSERT INTO Author (name, description) VALUES
('Isaac Asimov', 'A prolific science fiction writer and biochemist.'),
('J.K. Rowling', 'British author best known for the Harry Potter series.'),
('Malcolm Gladwell', 'Canadian journalist and author of non-fiction books.');

-- Insert Borrowers
INSERT INTO Borrower (name) VALUES
('Alice Johnson'),
('Bob Smith'),
('Charlie Nguyen');

-- Insert Books
INSERT INTO Books (id, title, description, present, borrower, author, publisher, genre) VALUES
(1, 'Foundation', 'A science fiction novel about the fall of a galactic empire.', FALSE, 'Alice Johnson', 1, 1, 1),
(2, 'Harry Potter and the Sorcerer`s Stone', 'A young wizard discovers his powers.', TRUE, NULL, 2, 1, 2),
(3, 'Outliers', 'A non-fiction book about success and the people who achieve it.', TRUE, NULL, 3, 2, 3),
(4, 'The Hobbit', 'A fantasy adventure preceding the Lord of the Rings.', FALSE, 'Bob Smith', 2, 3, 2);
