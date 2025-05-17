from psycopg2 import pool
import psycopg2.extras
from psycopg2 import sql

from dotenv import dotenv_values


# read .env
db_secrets = dotenv_values(".env")

# setup connection pool for thread safety
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=1,
    dbname="library_management",
    user=db_secrets["DB_USER"],
    password=db_secrets["DB_PASSWORD"],
    host="localhost",
    port="5432"
)

del db_secrets

borrowerid = -1

table_map = lambda table, entry: "CREATE (" + table.lower() + str(entry["id"]) + ":" + table + " {id:" + str(str(entry["id"])) + ", name:'" + entry["name"] + "', description: '" + entry["description"] + "'});\n"

def borrower_map(entry): 
    global borrowerid
    borrowerid += 1
    return "CREATE (borrower" + entry["name"].replace(" ", "") + ":Borrower {id: " + str(borrowerid) + ", name:'" + entry["name"] + "'});\n"

book_map = lambda entry: """
MATCH (author""" + str(entry["author"]) + """:Author {id:""" + str(entry["author"]) + """})
MATCH (genre""" + str(entry["genre"]) + """:Genre {id:""" + str(entry["genre"]) + """})
MATCH (publisher""" + str(entry["publisher"]) + """:Publisher {id:""" + str(entry["publisher"]) + """})

CREATE (book""" + str(entry["id"]) + """:Book {
        id:""" + str(entry["id"]) + """,
        title:'""" + entry["title"] + """',
        description:'""" + entry["description"] + """',
        present:""" + str(entry["present"]).lower() + """
})
CREATE (book""" + str(entry["id"]) + """)-[:WRITTEN_BY]->(author""" + str(entry["author"]) + """)
CREATE (book""" + str(entry["id"]) + """)-[:PUBLISHED_BY]->(publisher""" + str(entry["publisher"]) + """)
CREATE (book""" + str(entry["id"]) + """)-[:OF_GENRE]->(genre""" + str(entry["genre"]) + """);\n"""


if __name__ == '__main__':
    conn = db_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    init_script_content = []

    ### "Genre", "Publisher", "Author" tables
    for table in ("Genre", "Publisher", "Author"):
        cur.execute(f"SELECT * FROM {table};")
        items = cur.fetchall()
        
        for item in items:
            ### add to neo4j
            init_script_content.append(table_map(table, item))

    ### Borrowers table
    cur.execute(f"SELECT * FROM Borrower;")
    items = cur.fetchall()

    for item in items:
        ### add to neo4j
        init_script_content.append(borrower_map(item))

    ### Books table
    cur.execute(f"SELECT * FROM Books;")
    items = cur.fetchall()

    for item in items:
        ### add to neo4j
        init_script_content.append(book_map(item))

    cur.close()

    # Return connection to pool
    db_pool.putconn(conn)

    with open("db_init/data_neo4j.cypher", 'w') as f:
        f.writelines(init_script_content)