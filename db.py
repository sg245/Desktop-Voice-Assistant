import sqlite3

def connect():
    return sqlite3.connect("jarvis.db")

def create_users_table():
    conn = connect()
    cursor = conn.cursor()
    #remove condition not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (   
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()
    
def add_user(username, password):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

        
def set_current_user(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM current_user")
    cursor.execute("INSERT OR REPLACE INTO current_user (id, username) VALUES (1, ?)",(username,))

    conn.commit()
    conn.close()

def get_current_user():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM current_user LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def logout_current_user():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM current_user")  #update this delete option
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_current_user_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_user (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def init_db():
    create_users_table()
    create_current_user_table()

