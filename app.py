import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from skill_extractor import extract_skills

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        fullname = request.form["fullname"]
        email = request.form["email"]
        contact = request.form["contact"]
        domain = request.form["domain"]
        password = request.form["password"]
        repassword = request.form["repassword"]

        if password != repassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        resume_file = request.files.get("resume")
        resume_filename = None
        skills = ""

        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            resume_filename = username + "_" + filename
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_filename)
            resume_file.save(resume_path)
            skills = extract_skills(resume_path)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, fullname, email, contact, domain, password, resume, skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, fullname, email, contact, domain, hashed_password, resume_filename, skills),
            )
            conn.commit()
            conn.close()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists!", "danger")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return render_template("dashboard.html", user=user)

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return render_template("profile.html", user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        contact = request.form["contact"]
        domain = request.form["domain"]

        resume_file = request.files.get("resume")
        resume_filename = user["resume"]
        skills = user["skills"]

        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            resume_filename = user["username"] + "_" + filename
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_filename)
            resume_file.save(resume_path)
            skills = extract_skills(resume_path)

        conn.execute(
            "UPDATE users SET fullname=?, email=?, contact=?, domain=?, resume=?, skills=? WHERE id=?",
            (fullname, email, contact, domain, resume_filename, skills, session["user_id"]),
        )
        conn.commit()
        conn.close()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("edit_profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
