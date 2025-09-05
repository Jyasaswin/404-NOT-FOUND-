import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN domain TEXT")
except sqlite3.OperationalError:
    print("Column 'domain' already exists.")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN skills TEXT")
except sqlite3.OperationalError:
    print("Column 'skills' already exists.")

conn.commit()
conn.close()
print("Columns added successfully!")
