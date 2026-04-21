from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3
import bcrypt
import statbotics
sb = statbotics.Statbotics()

weak_passwords = [
    "123456",
    "admin",
    "12345678",
    "123456789",
    "1234",
    "12345",
    "password",
    "123",
    "Aa123456",
    "1234567890",
    "1234567",
    "123123",
    "111111",
    "Password",
    "12345678910",
    "000000",
    "Admin123",
    "********",
    "user",
    "qwerty"
]

list_of_special_characters = [
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "_",
    "+",
    "-",
    "=",
    "[",
    "]",
    "{",
    "}",
    "|",
    "\\",
    ":",
    ";",
    "'",
    "\"",
    "<",
    ">",
    ",",
    ".",
    "?",
    "/",
]

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def get_db(requested):
    conn = sqlite3.connect(requested)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Auth database
    conn_auth = get_db("auth.db")
    conn_auth.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn_auth.commit()
    conn_auth.close()

    # Following database
    conn_follow = get_db("following.db")
    conn_follow.execute("""
        CREATE TABLE IF NOT EXISTS following (
            username TEXT PRIMARY KEY,
            following_teams TEXT
        )
    """)
    conn_follow.commit()
    conn_follow.close()

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
.large-card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    width: 500px;
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

user_profile_page = base_style + """
<div class="card">
<h2> You are following teams:</h2>
{% if following_teams %}
<ul>
{% for team in following_teams %}
<a href="/team/{{ team }}"><p>Team {{ team }}</p></a>
{% endfor %}
</ul>
{% else %}
<p>No teams followed yet.</p>
{% endif %}
<a href="/add_team"><button>Add Team</button></a>
<a href="/remove_team"><button>Remove Team</button></a>
<a href="/logout"><button>Logout</button></a>
</div> 
"""

team_info_page = base_style + """
<div class="large-card">
{% if team %}
<h1> Team {{ team_number }}, {{ team['name'] }} Info </h1>
<p> Rookie Year: {{ team['rookie_year'] }} </p>
<p> This Season's EPA: {{ team['norm_epa']['current'] }} </p>
<p> Max EPA: {{ team['norm_epa']['max'] }} </p>
<p> Alltime Record: {{ team['record']['wins'] }} - {{ team['record']['losses'] }} </p>
<p> Winrate: {{ team['record']['winrate'] }}% </p>
{% else %}
<p> Team not found. </p>
{% endif %}
<a href="/profile"><button>Back to Profile</button></a>
</div>
"""

remove_team_page = base_style + """
<div class="card">
<h1> Remove Team </h1>
<form id="removeForm">
    <input name="number" placeholder="eg.254"><br>
    <button type="submit"> Remove Team </button>
</form>
</div>
<script>
document.getElementById('removeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const number = formData.get('number');
    fetch('/remove_team', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ number: number })
    }).then(response => {
        if (response.ok) {
            window.location.href = '/profile';
        } else {
            alert('Error removing team');
        }
    });
});
</script>
"""

add_team_page = base_style + """
<div class="card">
<h1> Add Team </h1>
<form id="addForm">
    <input name="number" placeholder="eg. 254"><br>
    <button type="submit"> Add Team </button>
</form>
</div>
<script>
document.getElementById('addForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const number = formData.get('number');
    fetch('/follow', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ number: number })
    }).then(response => {
        if (response.ok) {
            window.location.href = '/profile';
        } else {
            alert('Error adding team');
        }
    });
});
</script>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db("auth.db")
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
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
            # is_strong, message = check_password_strength(password,username)
            # if not is_strong:
            #     error = message
            # else:
                try:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    # Insert into auth.db
                    conn_auth = get_db("auth.db")
                    conn_auth.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, hashed_password)
                    )
                    conn_auth.commit()
                    conn_auth.close()
                    # Insert into following.db
                    conn_follow = get_db("following.db")
                    conn_follow.execute(
                        "INSERT INTO following (username, following_teams) VALUES (?, ?)",
                        (username, "")
                    )
                    conn_follow.commit()
                    conn_follow.close()
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    error = "Username already exists"

    return render_template_string(register_page, error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db("following.db")
    user = conn.execute(
        "SELECT * FROM following WHERE username=?",
        (session["user"],)
    ).fetchone()
    conn.close()
    following_teams = user["following_teams"].split(",") if user and user["following_teams"] else []
    return render_template_string(user_profile_page, username=session["user"], following_teams=following_teams)

@app.route("/add_team")
def add_team():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(add_team_page)

@app.route("/follow", methods=["PUT"])
def follow():
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    team_number = request.form.get("number", "").strip()
    if not team_number:
        return "Invalid team number", 400

    conn = get_db("following.db")
    user = conn.execute(
        "SELECT following_teams FROM following WHERE username = ?",
        (username,)
    ).fetchone()
    if user:
        current = user["following_teams"] or ""
        if current:
            updated = f"{current},{team_number}"
        else:
            updated = team_number
        conn.execute(
            "UPDATE following SET following_teams = ? WHERE username = ?",
            (updated, username)
        )
        conn.commit()
    conn.close()
    return "", 204

@app.route("/team/<team_number>")
def team_info(team_number):
    if "user" not in session:
        return redirect(url_for("login"))
    try:
        team_number = int(team_number)
    except ValueError:
        team = None
    else:
        try:
            team = sb.get_team(team_number)
        except Exception:
            team = None
    return render_template_string(team_info_page, team_number=team_number, team=team)

@ app.route("/remove_team", methods=["GET", "DELETE"])
def remove_team():
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    if request.method == "DELETE":
        team_number = request.form.get("number", "").strip()
        if not team_number:
            return "Invalid team number", 400

        conn = get_db("following.db")
        user = conn.execute(
            "SELECT following_teams FROM following WHERE username = ?",
            (username,)
        ).fetchone()
        if user:
            current = user["following_teams"] or ""
            teams = current.split(",") if current else []
            if team_number in teams:
                teams.remove(team_number)
                updated = ",".join(teams)
                conn.execute(
                    "UPDATE following SET following_teams = ? WHERE username = ?",
                    (updated, username)
                )
                conn.commit()
        conn.close()
        return "", 204  
    else:
        return render_template_string(remove_team_page)

def check_special_characters(password):
    for item in list_of_special_characters:
        if item in password:
            return True
    return False

def check_capital_letters(password):
    for char in password:
        if char.isupper():
            return True
    return False

def check_numbers(password):
    for char in password:
        if char.isdigit():
            return True
    return False

def check_weak_passwords(password):
    for wpass in weak_passwords:
        if wpass == password:
            return True
    return False

def check_password_strength(password,username=None):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if check_weak_passwords(password):
        return False, "Password is too common. Please choose a stronger password."
    if username and username.lower() in password.lower():
        return False, "Password should not contain your username."
    if not check_capital_letters(password):
        return False, "Password must contain at least one capital letter."
    if not check_numbers(password):
        return False, "Password must contain at least one number."
    if not check_special_characters(password):
        return False, "Password must contain at least one special character."
    return True, ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3966)
# Rocket_City_2026 = sb.get_team_event(3966,'2026alhu')
# print(Rocket_City_2026)
# sta0ts = sb.get_team_matches(3966,None,'2026alhu')
# print(sta0ts)
# ayaus = sb.get_team_events(3966, 2026)
# print(ayaus)