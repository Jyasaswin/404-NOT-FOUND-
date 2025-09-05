from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
            resume TEXT
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
        password = request.form["password"]
        repassword = request.form["repassword"]
        if password != repassword:
            return "Passwords do not match!"

        fullname = request.form["fullname"]
        contact = request.form["contact"]

        resume_file = request.files.get("resume")
        resume_filename = None
        if resume_file and resume_file.filename != "":
            resume_filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password, fullname, contact, resume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, hashed_password, fullname, contact, resume_filename))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
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
            session["user_id"] = user[0]
            session["username"] = user[1]
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

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    if request.method == "POST":
        fullname = request.form["fullname"]
        contact = request.form["contact"]
        skills = request.form.get("skills", "")

        # Handle resume upload
        resume_file = request.files.get("resume")
        if resume_file and resume_file.filename != "":
            resume_filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))
            c.execute("UPDATE users SET resume=? WHERE id=?", (resume_filename, session["user_id"]))

        c.execute("""
            UPDATE users 
            SET fullname=?, contact=?, skills=?
            WHERE id=?
        """, (fullname, contact, skills, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))

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
