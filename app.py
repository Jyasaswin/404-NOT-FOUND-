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
            c = conn.cursor()
            
             # Check if user already exists
            c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
            existing = c.fetchone()
            if existing:
                conn.close()
                flash("User already exists! Please log in.", "danger")
                return redirect(url_for("login"))

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
            session["user_id"] = user[0]      # store user id
            session["username"] = user[1]     # store username
            flash("You are logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials!"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/add_skills", methods=["GET", "POST"])
def add_skills():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Collect all fields from multi-step form
        fullname = request.form.get("fullname")
        age = request.form.get("age")
        contact = request.form.get("contact")
        bio = request.form.get("bio")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        availability = request.form.get("availability")
        role = request.form.get("role")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""UPDATE users 
                     SET fullname=?, age=?, contact=?, bio=?, skills=?, interests=?, availability=?, role=?
                     WHERE id=?""",
                  (fullname, age, contact, bio, skills, interests, availability, role, session["user_id"]))
        conn.commit()
        conn.close()

        flash("Profile completed successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_skills.html")


@app.route("/add_personal", methods=["GET", "POST"])
def add_personal():
    if "user_id" not in session:
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
                     WHERE id=?""",
                  (fullname, age, contact, bio, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Personal details added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_personal.html")

@app.route("/add_other", methods=["GET", "POST"])
def add_other():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        interests = request.form.get("interests")
        availability = request.form.get("availability")
        role = request.form.get("role")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""UPDATE users 
                     SET interests=?, availability=?, role=? 
                     WHERE id=?""",
                  (interests, availability, role, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Other details added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_other.html")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    user = c.fetchone()
    conn.close()
    return render_template("profile.html", user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        fullname = request.form["fullname"]
        age = request.form["age"]
        contact = request.form["contact"]
        bio = request.form["bio"]
        skills = request.form["skills"]
        interests = request.form["interests"]
        availability = request.form["availability"]
        role = request.form["role"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""UPDATE users 
                     SET fullname=?, age=?, contact=?, bio=?, skills=?, interests=?, availability=?, role=? 
                     WHERE id=?""",
                  (fullname, age, contact, bio, skills, interests, availability, role, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = c.fetchone()
    conn.close()
    return render_template("edit_profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
