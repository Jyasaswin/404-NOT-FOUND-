import sqlite3

def show_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, fullname, contact, domain, skills, resume FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("No users found in the database.")
    else:
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Username: {user[1]}")
            print(f"Email: {user[2]}")
            print(f"Full Name: {user[3]}")
            print(f"Contact: {user[4]}")
            print(f"Domain: {user[5]}")
            print(f"Skills: {user[6]}")
            print(f"Resume File: {user[7]}")
            print("-" * 40)
    
    conn.close()

if __name__ == "__main__":
    show_users()
