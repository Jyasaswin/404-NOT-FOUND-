import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
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

def normalize_skills(skill_string):
    if not skill_string:
        return set()
    return set(s.strip().lower() for s in skill_string.split(",") if s.strip())


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
            skills = ",".join(normalize_skills(extract_skills(resume_path)))

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
            skills = ",".join(normalize_skills(extract_skills(resume_path)))

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


@app.route("/resume/<filename>")
def download_resume(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/match")
def match():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cur.fetchone()
    if not user:
        conn.close()
        return "User not found", 404

    user_skills = normalize_skills(user["skills"])
    user_domain = user["domain"]

    cur.execute("SELECT * FROM domains WHERE LOWER(name)=?", (user_domain.lower(),))
    domain = cur.fetchone()
    if not domain:
        conn.close()
        return f"No domain setup for {user_domain}", 404

    required_skills = normalize_skills(domain["required_skills"])
    missing_skills = list(required_skills - user_skills)

    cur.execute("SELECT * FROM users WHERE domain=? AND id!=?", (user_domain, user["id"]))
    teammates = cur.fetchall()

    suggestions = []
    for t in teammates:
        t_skills = normalize_skills(t["skills"])
        overlap = len(set(missing_skills) & t_skills)
        score = int((overlap / len(required_skills)) * 100) if required_skills else 0
        suggestions.append({
            "id": t["id"],
            "username": t["username"],
            "fullname": t["fullname"],
            "skills": t["skills"],
            "domain": t["domain"],
            "match_score": score
        })

    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    conn.close()
    return render_template("match.html", user_skills=user_skills, missing_skills=missing_skills, suggestions=suggestions)


@app.route("/view_user/<int:user_id>")
def view_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()

    if not user:
        return "User not found", 404

    return render_template("view_user.html", user=user)


@app.route("/invite/<int:teammate_id>", methods=["POST"])
def invite(teammate_id):
    if "user_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("login"))

    sender_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM invites 
        WHERE (sender_id=? AND receiver_id=?) 
           OR (sender_id=? AND receiver_id=?)
    """, (sender_id, teammate_id, teammate_id, sender_id))
    existing = cursor.fetchone()

    if existing:
        flash("An invite already exists between you and this teammate!", "warning")
    else:
        cursor.execute(
            "INSERT INTO invites (sender_id, receiver_id, status) VALUES (?, ?, ?)",
            (sender_id, teammate_id, "pending")
        )
        conn.commit()
        flash("Invite sent successfully ✅", "success")

    conn.close()
    return redirect(url_for("match"))

@app.route("/respond_invite/<int:invite_id>/<string:action>", methods=["POST"])
def respond_invite(invite_id, action):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT sender_id, receiver_id FROM invites WHERE id=?", (invite_id,))
    invite = cursor.fetchone()
    if not invite:
        conn.close()
        flash("Invite not found!", "danger")
        return redirect(url_for("my_invites"))

    sender_id, receiver_id = invite

    if action == "accept":
        cursor.execute("UPDATE invites SET status='accepted' WHERE id=?", (invite_id,))
       
    else:
        cursor.execute("UPDATE invites SET status='rejected' WHERE id=?", (invite_id,))

    conn.commit()
    conn.close()
    flash(f"Invite {action}ed successfully!", "success")
    return redirect(url_for("my_invites"))

@app.route("/my_invites")
def my_invites():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    invites = conn.execute("""
        SELECT invites.id, users.username AS sender, invites.status
        FROM invites
        JOIN users ON invites.sender_id = users.id
        WHERE invites.receiver_id = ?
    """, (session["user_id"],)).fetchall()
    conn.close()
    return render_template("my_invites.html", invites=invites)


@app.route("/teams")
def teams():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    teams_list = conn.execute("""
        SELECT t.id, t.name, t.created_by
        FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.user_id=?
    """, (session["user_id"],)).fetchall()

    team_data = []
    for t in teams_list:
        members = conn.execute("""
            SELECT u.id, u.username, u.fullname, u.skills, u.domain
            FROM users u
            JOIN team_members tm ON u.id = tm.user_id
            WHERE tm.team_id=?
        """, (t["id"],)).fetchall()
        team_data.append({"team": t, "members": members})

    conn.close()
    return render_template("teams.html", team_data=team_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
