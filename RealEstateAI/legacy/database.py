import sqlite3

DB_PATH = "database/users.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()

    return user