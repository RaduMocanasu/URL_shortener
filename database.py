import sqlite3

# opens a connection to the database. it is a channel which allows us to send commands to the database
def get_connection():
    return sqlite3.connect("urls.db")

# creates the sql tables
def create_tables():
    connection = get_connection()

    # creates a table named urls, with 2 columns : code, original_url. code is a unique identifier(primary key). url must contain a value, it can't be null
    connection.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL
        )
    """)

    #saves the database changes permanently
    connection.commit()
    connection.close()

# saves the url to the database
def save_url(code : str, original_url : str):
    connection = get_connection()

    # inserts a new row into the database. the ? characters are placeholders(like %d in printf, or {arg} in f strings)
    connection.execute(
        "Insert INTO urls (code, original_url) VALUES (?, ?)",
        (code, original_url)
    )

    # saves changes
    connection.commit()
    connection.close()

# gets the long url for the code
def get_url(code : str):
    connection = get_connection()

    # finds the original_url from the urls table where 'code' is equal to a given value 
    cursor = connection.execute(
        "SELECT original_url FROM urls WHERE code = ?",
        (code,)
    )

    # gets the first matching row
    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    # the row is a tuple, of type ("url...",), so we only need the first field
    return row[0]


