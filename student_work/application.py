from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            following_teams TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


base_style = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 300px;
    text-align: center;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
}
button {
    padding: 10px;
    width: 60%;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
button:hover {
    background: #45a049;
}
a {
    display: block;
    margin-top: 10px;
    color: #333;
    text-decoration: none;
}
.error {
    color: red;
    margin-top: 10px;
}
</style>
"""

login_page = base_style + """
<div class="card">
<h2>Login</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>
<a href="/register">Create an account</a>
<p class="error">{{ error }}</p>
</div>
"""

register_page = base_style + """
<div class="card">
<h2>Register</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Sign Up</button>
</form>
<a href="/">Back to login</a>
<p class="error">{{ error }}</p>
</div>
"""

secret_page = base_style + """
<div class="card">
<h2>🎉 Secret Room</h2>
<h3>Welcome, {{ username }}!</h3>
<p>You got into the secret room!</p>
<a href="/logout"><button>Logout</button></a>
</div>
"""


user_profile_page = base_style + """
<div class="card">
<h2> You are following teams:</h2>
{% if following_teams %}
<ul>
{% for team in following_teams %}
<a href="/team/{{ team }}"><li>Team {{ team }}</li></a>
{% endfor %}
</ul>
{% else %}
<p>No teams followed yet.</p>
{% endif %}
<a href="/add_team">Add Team</a>
<a href="/logout"><button>Logout</button></a>
</div> 
"""

team_info_page = base_style + """
<div class="card">
<h1> Team {{ team_number }} Info </h1>
<p>Team {{ team_number }} is a great team!</p>
<a href="/profile"><button>Back to Profile</button></a>
</div>
"""

add_team_page = base_style + """
<div class="card">
<h1> Add Team </h1>
<form method="POST" action="/follow">
    <input name="number" placeholder="eg. 254"><br>
    <button type="submit"> Add Team </button>
</form>
</div>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and user["password"] == password:
            session["user"] = username
            return redirect(url_for("profile"))
        else:
            error = "Incorrect username or password"

    return render_template_string(login_page, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if not username or not password:
            error = "Fields cannot be empty"
        else:
            try:
                conn = get_db()
                conn.execute(
                    "INSERT INTO users (username, password, following_teams) VALUES (?, ?, ?)",
                    (username, password, "")
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists"

    return render_template_string(register_page, error=error)

@app.route("/secret")
def secret():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(secret_page, username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()
    conn.close()
    following_teams = user["following_teams"].split(",") if user["following_teams"] else []
    return render_template_string(user_profile_page, username=session["user"], following_teams=following_teams)

@app.route("/add_team")
def add_team():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(add_team_page)

@app.route("/follow", methods=["POST"])
def follow():
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    team_number = request.form.get("number", "").strip()
    if not team_number:
        return redirect(url_for("profile"))

    conn = get_db()
    user = conn.execute(
        "SELECT following_teams FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    if user:
        current = user["following_teams"] or ""
        if current:
            updated = f"{current},{team_number}"
        else:
            updated = team_number
        conn.execute(
            "UPDATE users SET following_teams = ? WHERE username = ?",
            (updated, username)
        )
        conn.commit()
    conn.close()
    return redirect(url_for("profile"))

@app.route("/team/<team_number>")
def team_info(team_number):
    return render_template_string(team_info_page, team_number=team_number)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3966)