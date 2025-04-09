CREATE TABLE Genre (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40),
    description VARCHAR(1000)
);

CREATE TABLE Publisher (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40),
    description VARCHAR(1000)
);

CREATE TABLE Author (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40),
    description VARCHAR(1000)
);

CREATE TABLE Borrower (
    name VARCHAR(40) PRIMARY KEY
);

CREATE TABLE Books (
    id INTEGER PRIMARY KEY,
    title VARCHAR(80),
    description VARCHAR(1000),
    present BOOLEAN DEFAULT 'TRUE',
    borrower VARCHAR(40),
    author INTEGER,
    publisher INTEGER,
    genre INTEGER,
    borrowDate DATE,
    returnDate DATE, 
    FOREIGN KEY (borrower) REFERENCES Borrower(name) ON DELETE SET NULL,
    FOREIGN KEY (author) REFERENCES Author(id) ON DELETE SET NULL,
    FOREIGN KEY (publisher) REFERENCES Publisher(id) ON DELETE SET NULL,
    FOREIGN KEY (genre) REFERENCES Genre(id) ON DELETE SET NULL
);
