CREATE (genre1:Genre {id:1, name:'Science Fiction', description: ''});
CREATE (genre2:Genre {id:2, name:'Fantasy', description: 'Stories involving magical elements and fantastical worlds'});
CREATE (genre3:Genre {id:3, name:'Non-fiction', description: ''});
CREATE (publisher1:Publisher {id:1, name:'Orbit Books', description: ''});
CREATE (publisher2:Publisher {id:2, name:'Penguin Random House', description: ''});
CREATE (publisher3:Publisher {id:3, name:'HarperCollins', description: 'A major publisher of fiction and non-fiction books.'});
CREATE (author1:Author {id:1, name:'Isaac Asimov', description: ''});
CREATE (author2:Author {id:2, name:'J.K. Rowling', description: ''});
CREATE (author3:Author {id:3, name:'Malcolm Gladwell', description: 'Canadian journalist and author of non-fiction books.'});
CREATE (borrowerAliceJohnson:Borrower {id: 0, name:'Alice Johnson'});
CREATE (borrowerBobSmith:Borrower {id: 1, name:'Bob Smith'});
CREATE (borrowerCharlieNguyen:Borrower {id: 2, name:'Charlie Nguyen'});

MATCH (author1:Author {id:1})
MATCH (genre1:Genre {id:1})
MATCH (publisher1:Publisher {id:1})

CREATE (book1:Book {
        id:1,
        title:'Foundation',
        description:'',
        present:false
})
CREATE (book1)-[:WRITTEN_BY]->(author1)
CREATE (book1)-[:PUBLISHED_BY]->(publisher1)
CREATE (book1)-[:OF_GENRE]->(genre1);

MATCH (author2:Author {id:2})
MATCH (genre2:Genre {id:2})
MATCH (publisher1:Publisher {id:1})

CREATE (book2:Book {
        id:2,
        title:'Harry Potter and the Sorcerers Stone',
        description:'',
        present:true
})
CREATE (book2)-[:WRITTEN_BY]->(author2)
CREATE (book2)-[:PUBLISHED_BY]->(publisher1)
CREATE (book2)-[:OF_GENRE]->(genre2);

MATCH (author3:Author {id:3})
MATCH (genre3:Genre {id:3})
MATCH (publisher2:Publisher {id:2})

CREATE (book3:Book {
        id:3,
        title:'Outliers',
        description:'',
        present:true
})
CREATE (book3)-[:WRITTEN_BY]->(author3)
CREATE (book3)-[:PUBLISHED_BY]->(publisher2)
CREATE (book3)-[:OF_GENRE]->(genre3);

MATCH (author2:Author {id:2})
MATCH (genre2:Genre {id:2})
MATCH (publisher3:Publisher {id:3})

CREATE (book4:Book {
        id:4,
        title:'The Hobbit',
        description:'',
        present:false
})
CREATE (book4)-[:WRITTEN_BY]->(author2)
CREATE (book4)-[:PUBLISHED_BY]->(publisher3)
CREATE (book4)-[:OF_GENRE]->(genre2);
