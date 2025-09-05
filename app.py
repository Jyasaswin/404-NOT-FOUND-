from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            skills TEXT,
            fullname TEXT,
            age INTEGER,
            contact TEXT,
            bio TEXT,
            interests TEXT,
            availability TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return "User already exists!"
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["username"] = username
            flash("You are logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials!"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/add_skills", methods=["GET", "POST"])
def add_skills():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        skills = request.form.get("skills")
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("UPDATE users SET skills=? WHERE username=?", (skills, session["username"]))
        conn.commit()
        conn.close()
        flash("Skills added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_skills.html")

@app.route("/add_personal", methods=["GET", "POST"])
def add_personal():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        age = request.form.get("age")
        contact = request.form.get("contact")
        bio = request.form.get("bio")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""UPDATE users 
                     SET fullname=?, age=?, contact=?, bio=? 
                     WHERE username=?""",
                  (fullname, age, contact, bio, session["username"]))
        conn.commit()
        conn.close()
        flash("Personal details added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_personal.html")

@app.route("/add_other", methods=["GET", "POST"])
def add_other():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        interests = request.form.get("interests")
        availability = request.form.get("availability")
        role = request.form.get("role")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""UPDATE users 
                     SET interests=?, availability=?, role=? 
                     WHERE username=?""",
                  (interests, availability, role, session["username"]))
        conn.commit()
        conn.close()
        flash("Other details added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_other.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
