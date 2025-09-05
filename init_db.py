import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT,
            contact TEXT,
            resume TEXT,
            skills TEXT,
            domain TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized and table ensured!")

if __name__ == "__main__":
    init_db()
