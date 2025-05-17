# library_management_task
Basic Library Management System 

## Exercise 1:
- ER-Diagram.pdf for the diagram
- ER-Diagram.md for the dokumentation

## Exercise 2:
### Setup:
- Schema and initial data can be found in /db_init
- specify DB_USER and DB_PASSWORD in a .env file and run docker-compose for db setup.
### Notable implementation enhancements:
- added a book search form (client side)
- use of a connection pool for increased efficiency

## Exercise 3:
### Modeling:
- Book, Borrower, Genre, Author, Publisher as nodes
- borrowed by as edges
- relationships between book and author, genre, ... as edges as well
### Migration:
I used a migration script (migration.py) that converts the sql database into a .cypher data initalization script for neo4j. That script is ran when the container starts. I kept the neo4j 'schema' quite flexible as modelling more constrainst required an enterprise edition. 
