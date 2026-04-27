
from flask import Flask, request, redirect, render_template_string, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "salainen"


UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Keskustelualue</title>
    <style>
    body {
        background-image: url('/static/kukat.jpg');
        background-size: cover;      
        background-position: center; 
        background-repeat: no-repeat;
        margin: 0;
        padding: 20px 0;            
        font-family: Arial, sans-serif;
        min-height: 100vh;          
    }
    .container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
        max-width: 900px;
        width: 90%;
        margin: 0 auto;             
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }


    .message { display: flex; align-items: center; font-size: 14px; }
    .theme { font-size: 12px; color: gray; margin-left: 5px; }
    .trash-btn { background: none; border: none; padding: 0 5px; cursor: pointer; }
    .trash-btn img { width: 16px; height: 16px; }
    img { max-width: 200px; max-height: 200px; margin-left: 10px; }
        .trash-btn { background: none; border: none; padding: 0 5px; cursor: pointer; }
        .trash-btn img { width: 16px; height: 16px; }
        img { max-width: 200px; max-height: 200px; margin-left: 10px; }
    </style>
</head>
<body>
<div class="container">

<h1 style="text-align: center;">TERVETULOA OPISKELIJABLOGIIN!</h1>

<div style="display: flex; justify-content: space-between; align-items: center;">
{% if session.username %}
<p>Kirjautunut käyttäjä: {{ session.username }}</p>
<a href="/logout">Kirjaudu ulos</a>
{% endif %}
</div>

<p>Sivua ladattu: {{ visits }} kertaa</p>
<form method="get" action="/">
    <input name="search" placeholder="Etsi käyttäjä tai blogi">
    <input type="submit" value="Hae">
</form>

<h2>Uusimmat</h2>
<div style="max-height: 300px; overflow-y: scroll; border:1px solid #aaa; padding:10px;">
{% for post_id, title, content, image_path, theme, username in posts %}
    <div style="margin-bottom:15px;">
        <strong><a href="/user/{{ username }}">{{ username }}</a></strong> - <em>{{ title }}</em> ({{ theme }})<br>
        {{ content }}<br>
        {% if image_path %}
            <img src="{{ image_path }}" style="max-width:200px;">
        {% endif %}
    </div>
{% endfor %}
</div>

<h3>Valitse aihe</h3>
<a href="/">Kaikki</a> |
<a href="/?theme=opiskelu">Opiskelu</a> |
<a href="/?theme=vapaa-aika">Vapaa-aika</a> |
<a href="/?theme=musiikki">Musiikki</a> |
<a href="/?theme=urheilu">Urheilu</a> |
<a href="/?theme=lukeminen">Lukeminen</a> |
<a href="/?theme=pelit">Pelit</a>

<h3>Keskustelualue</h3>
<ul>
{% for content, msg_id, image_path, username, theme in messages %}
    <li class="message">
        <strong><a href="/user/{{ username }}">{{ username }}</a>:</strong> {{ content }}
        <span class="theme">({{ theme }})</span>
        {% if image_path %}
            <img src="{{ image_path }}" alt="Ladattu kuva">
        {% endif %}
        <form action="/delete/{{ msg_id }}" method="post" style="display:inline;">
            <button class="trash-btn" type="submit">
                <img src="/static/trashbin.png" alt="Poista">
            </button>
        </form>
    </li>
{% endfor %}
</ul>

<a href="/new">Lähetä uusi viesti</a> | <a href="/posts">Postaukset</a>

</div>
</body>
</html>
"""

NEW_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Uusi viesti</title>
</head>
<body>
<h1>Uusi viesti</h1>

<form action="/send" method="post" enctype="multipart/form-data">
<textarea name="content" rows="4" cols="40" placeholder="Kirjoita viesti..."></textarea><br><br>
Lisää kuva (valinnainen): <input type="file" name="image"><br><br>
Teema:<br>
<select name="theme">
    <option value="opiskelu">Opiskelu</option>
    <option value="vapaa-aika">Vapaa-aika</option>
    <option value="musiikki">Musiikki</option>
    <option value="elokuvat/sarjat">Elokuvat/Sarjat</option>
    <option value="urheilu">Urheilu</option>
    <option value="lukeminen">Lukeminen</option>
    <option value="pelit">Pelit</option>
</select><br><br>
<input type="submit" value="Lähetä">
</form>



<br>
<a href="/">Takaisin keskusteluun</a>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Kirjaudu</title>
</head>
<style>
body {
    background-image: url('/static/kukat.jpg');
    background-size: cover;      
    background-position: center; 
    background-repeat: no-repeat;
    margin: 0;
    padding: 0;            
    font-family: Arial, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column; 
    align-items: center;     
}

header {
    width: 100%
    text-align: center;
    padding: 40px 0 20px 0;
    font-size: 32px;
    color: #fff;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}

.container {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 10px;
    max-width: 400px;  
    width: 90%;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    margin-top: auto;
    margin-bottom: auto;
    text-align: center; 
}

input[type="text"], input[type="password"] {
    width: 80%;
    padding: 10px;
    margin: 8px 0;
    border-radius: 5px
    border: 1px solid
}

input[type="submit"] {
    padding: 10px 20px;
    margin-top: 10px;
    border-radius: 5px;
    border: none;
    background-color: #4285F4;
    color: white;
    cursor: pointer;
}
input[type="submit"]:hover {
    background-color: #357ae8;
}
</style>

<h1 style="text-align: center;">Kirjaudu opiskelijablogiin</h1>
<div style="text-align: center;">
<form action="/login" method="post">
Käyttäjänimi:<br>
<input name="username"><br><br>

Salasana:<br>
<input type="password" name="password"><br><br>

<input type="submit" value="Kirjaudu">
</form>
</div>

<br>
<a href="/register">Rekisteröidy</a>

</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Rekisteröidy</title>
</head>
<body>

<h1>Luo käyttäjä</h1>

<form action="/create_user" method="post">
Käyttäjänimi:<br>
<input name="username"><br><br>

Blogin nimi:<br>
<input name="blog_name"><br><br>


Salasana:<br>
<input type="password" name="password"><br><br>

Toista salasana:<br>
<input type="password" name="password2"><br><br>

<input type="submit" value="Rekisteröidy">
</form>

</body>
</html>
"""

POST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Uusi postaus</title>
</head>
<body>
<h1>Luo uusi postaus</h1>

<form action="/post_send" method="post" enctype="multipart/form-data">
Otsikko:<br><input name="title"><br><br>
Teksti:<br>
<textarea name="content" rows="4" cols="40"></textarea><br><br>
Teema:<br>
<select name="theme">
    <option value="opiskelu">Opiskelu</option>
    <option value="vapaa-aika">Vapaa-aika</option>
    <option value="musiikki">Musiikki</option>
    <option value="elokuvat/sarjat">Elokuvat/Sarjat</option>
    <option value="urheilu">Urheilu</option>
    <option value="lukeminen">Lukeminen</option>
    <option value="pelit">Pelit</option>
</select><br><br>
Kuva (valinnainen): <input type="file" name="image"><br><br>
<input type="submit" value="Julkaise">
</form>

<br>
<a href="/posts">Takaisin postauksiin</a>
</body>
</html>
"""

POSTS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Postaukset</title>
    <style>
        .post { border: 1px solid #aaa; padding: 10px; margin-bottom: 10px; }
        img { max-width: 300px; max-height: 300px; display:block; margin-top:5px; }

        .trash-btn {
            background: none;
            border: none;
            cursor: pointer;
        }
        .trash-btn img {
            width: 16px;
            height: 16px;
        }
    </style>
</head>
<body>
<h1>Postaukset</h1>
{% for post_id, title, content, image_path, theme, username in posts %}
<div class="post">
    <strong>{{ username }}</strong> - <em>{{ title }}</em> - <span>({{ theme }})</span><br>
    {{ content }}<br>

    <h4>Kommentit</h4>

    {% for c_post_id, c_content, c_username in comments %}
        {% if c_post_id == post_id %}
            <div style="margin-left:20px;">
                <strong>{{ c_username }}:</strong> {{ c_content }}
            </div>
        {% endif %}
    {% endfor %}

    <form method="post" action="/comment/{{ post_id }}">
        <input name="content" placeholder="Kirjoita kommentti">
        <button type="submit">Kommentoi</button>
    </form>

    <form action="/post_delete/{{ post_id }}" method="post" style="display:inline;">
        <button class="trash-btn" type="submit">
            <img src="/static/trashbin.png" alt="Poista">
        </button>
    </form>

    {% if image_path %}
        <img src="{{ image_path }}" alt="Kuva">
    {% endif %}
</div>
{% endfor %}

<a href="/post_new">Luo uusi postaus</a> | <a href="/">Keskustelualue</a>
</body>
</html>
"""


@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")
    db = sqlite3.connect("database.db", check_same_thread=False)
    search = request.args.get("search")
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    db.commit()

    visits = db.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    if search:
        posts = db.execute("""
            SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE users.username LIKE ? OR users.blog_name LIKE ?
            ORDER BY posts.created_at DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()
    else:
        posts = db.execute("""
            SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT 10
        """).fetchall()

    selected_theme = request.args.get("theme")

    if search:
        messages = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE users.username LIKE ? OR users.blog_name LIKE ?
        ORDER BY messages.id DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()

    elif selected_theme:
        messages = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE messages.theme = ?
            ORDER BY messages.id DESC
        """, (selected_theme,)).fetchall()

    else:
        messages = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            ORDER BY messages.id DESC
        """).fetchall()
    db.close()

    return render_template_string(INDEX_HTML, visits=visits, messages=messages, posts=posts, session=session)

@app.route("/new")
def new():
    if "username" not in session:
        return redirect("/login")
    return render_template_string(NEW_HTML)

@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return redirect("/login")

    content = request.form["content"].strip()
    image = request.files.get("image")
    theme = request.form.get("theme")

    if content == "":
        return redirect("/new")

    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("INSERT INTO messages (content, user_id, theme) VALUES (?, ?, ?)",
                 [content, session["user_id"], theme]
    )

    db.commit()

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        db.execute("UPDATE messages SET image_path = ? WHERE id = (SELECT MAX(id) FROM messages)", [image_path])
        db.commit()

    db.close()
    return redirect("/")


@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    if "username" not in session:
        return redirect("/login")
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("DELETE FROM messages WHERE id = ? AND user_id = ?", 
                (msg_id, session["user_id"])
    )
    db.commit()
    db.close()
    return redirect("/")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)

    username = request.form["username"]
    password = request.form["password"]

    db = sqlite3.connect("database.db", check_same_thread=False)
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE username=?",
        (username,)
    ).fetchone()
    db.close()
    if user and check_password_hash(user[1], password):
        session["user_id"] = user[0]
        session["username"] = username
        return redirect("/")
    else:
        return "Väärä käyttäjänimi tai salasana"

    



@app.route("/register")
def register():
    return render_template_string(REGISTER_HTML)

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    blog_name = request.form["blog_name"]
    password = request.form["password"]
    password2 = request.form["password2"]

    if password != password2:
        return "Salasanat eivät täsmää. <a href='/register'>Yritä uudelleen</a>"

    db = sqlite3.connect("database.db", check_same_thread=False)
    password_hash = generate_password_hash(password)
    db.execute("INSERT INTO users (username, password_hash, blog_name) VALUES (?, ?, ?)", (username, password_hash, blog_name))
    db.commit()
    db.close()

    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/post_new")
def post_new():
    if "username" not in session:
        return redirect("/login")
    return render_template_string(POST_HTML)

@app.route("/post_send", methods=["POST"])
def post_send():
    if "username" not in session:
        return redirect("/login")

    title = request.form["title"].strip()
    content = request.form["content"].strip()
    image = request.files.get("image")
    theme = request.form.get("theme")
    image_path = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("INSERT INTO posts (user_id, title, content, image_path, theme) VALUES (?, ?, ?, ?, ?)",
               (session["user_id"], title, content, image_path, theme))
    db.commit()
    db.close()

    return redirect("/posts")

@app.route("/posts")
def posts():
    if "username" not in session:
        return redirect("/login")
    db = sqlite3.connect("database.db", check_same_thread=False)
    posts = db.execute("""
        SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """).fetchall()

    comments = db.execute("""
        SELECT comments.post_id, comments.content, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.created_at
    """).fetchall()

    db.close()

    return render_template_string(POSTS_HTML, posts=posts, comments=comments)

@app.route("/post_delete/<int:post_id>", methods=["POST"])
def post_delete(post_id):
    if "username" not in session:
        return redirect("/login")
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("""
        DELETE FROM posts
        WHERE id = ? AND user_id = ?
    """, (post_id, session["user_id"]))
    db.commit()
    db.close()
    return redirect("/posts")

@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if "username" not in session:
        return redirect("/login")
    
    content = request.form["content"].strip()

    if content == "":
        return redirect("/posts")
    
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("""
        INSERT INTO comments (post_id, user_id, content)
        VALUES (?, ?, ?)
    """, (post_id, session["user_id"], content))

    db.commit()
    db.close()

    return redirect("/posts")
    


@app.route("/user/<username>")
def user_profile(username):
    if "username" not in session:
        return redirect("/login")
    
    db = sqlite3.connect("database.db", check_same_thread=False)

    posts = db.execute("""
        SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE users.username = ?
        ORDER BY posts.created_at DESC
    """, (username,)).fetchall()

    user = db.execute("SELECT blog_name FROM users WHERE username = ?", (username,)).fetchone()
    blog_name = user[0] if user else ""

    comments = db.execute("""
        SELECT comments.post_id, comments.content, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id IN (
            SELECT id FROM posts WHERE user_id = (SELECT id FROM users WHERE username = ?)
        )
        ORDER BY comments.created_at
    """, (username,)).fetchall()


    db.close()

    return render_template_string("""
    <h1>{{ username }} - {{ blog_name }}</h1>
    
    {% for post_id, title, content, image_path, theme, username in posts %}
        <div style="border:1px solid #aaa; padding:10px; margin-bottom:20px;">
            <strong>{{ username }}</strong> - <em>{{ title }}</em> ({{ theme }})<br>
            {{ content }}<br>
            
            {% if image_path %}
                <img src="/{{ image_path }}" style="max-width:300px;">
            {% endif %}
            
            <h4>Kommentit</h4>
            {% for c_post_id, c_content, c_username in comments %}
                {% if c_post_id == post_id %}
                    <div style="margin-left:20px;">
                        <strong>{{ c_username }}:</strong> {{ c_content }}
                    </div>
                {% endif %}
            {% endfor %}
            <form method="post" action="/comment/{{ post_id }}" style="margin-top:10px;">
                <input name="content" placeholder="Kirjoita kommentti" style="width:80%;">
                <button type="submit">Kommentoi</button>
            </form>
        </div>
    {% endfor %}
    <a href="/">Takaisin</a>
    """, posts=posts, comments=comments, username=username, blog_name=blog_name)
   

if __name__ == "__main__":
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY, visited_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)")
    db.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        image_path TEXT,
        theme TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        ID INTEGER PRIMARY KEY,
        content TEXT,
               image_path TEXT,
               user_id INTEGER,
               theme TEXT
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        post_id INTEGER,
        user_id INTEGER,
        content TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    db = sqlite3.connect("database.db", check_same_thread=False)


    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "blog_name" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN blog_name TEXT")
        db.commit()

    
    db.close()

if __name__ == "__main__":
    if not os.path.exists("database.db"):
        with sqlite3.connect("database.db") as db:
            with open("schema.sql") as f:
                db.executescript(f.read())


    app.run(debug=True)