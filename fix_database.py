import pathlib

pathlib.Path('database/users.py').write_text(
'''import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_by_username(username):
    db = sqlite3.connect("database.db", check_same_thread=False)
    user = db.execute(
        "SELECT id, password_hash FROM users WHERE username=?",
        (username,)
    ).fetchone()
    db.close()
    return user


def create_user(username, blog_name, password):
    db = sqlite3.connect("database.db", check_same_thread=False)
    password_hash = generate_password_hash(password)
    db.execute(
        "INSERT INTO users (username, password_hash, blog_name) VALUES (?, ?, ?)",
        (username, password_hash, blog_name)
    )
    db.commit()
    db.close()


def get_blog_name(username):
    db = sqlite3.connect("database.db", check_same_thread=False)
    user = db.execute("SELECT blog_name FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user[0] if user else ""


def check_password(user, password):
    return check_password_hash(user[1], password)
''', encoding="utf-8")

pathlib.Path('database/messages.py').write_text(
'''import sqlite3


def get_messages(search=None, theme=None):
    db = sqlite3.connect("database.db", check_same_thread=False)
    if search:
        rows = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE users.username LIKE ? OR users.blog_name LIKE ?
            ORDER BY messages.id DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()
    elif theme:
        rows = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE messages.theme = ?
            ORDER BY messages.id DESC
        """, (theme,)).fetchall()
    else:
        rows = db.execute("""
            SELECT messages.content, messages.id, messages.image_path, users.username, messages.theme
            FROM messages
            JOIN users ON messages.user_id = users.id
            ORDER BY messages.id DESC
        """).fetchall()
    db.close()
    return rows


def add_message(content, user_id, theme, image_path=None):
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute(
        "INSERT INTO messages (content, user_id, theme) VALUES (?, ?, ?)",
        [content, user_id, theme]
    )
    db.commit()
    if image_path:
        db.execute(
            "UPDATE messages SET image_path = ? WHERE id = (SELECT MAX(id) FROM messages)",
            [image_path]
        )
        db.commit()
    db.close()


def delete_message(msg_id, user_id):
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute(
        "DELETE FROM messages WHERE id = ? AND user_id = ?",
        (msg_id, user_id)
    )
    db.commit()
    db.close()
''', encoding="utf-8")

pathlib.Path('database/blogs.py').write_text(
'''import sqlite3


def get_posts(search=None, limit=10):
    db = sqlite3.connect("database.db", check_same_thread=False)
    if search:
        rows = db.execute("""
            SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE users.username LIKE ? OR users.blog_name LIKE ?
            ORDER BY posts.created_at DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()
    else:
        rows = db.execute("""
            SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
    db.close()
    return rows


def get_all_posts():
    db = sqlite3.connect("database.db", check_same_thread=False)
    rows = db.execute("""
        SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """).fetchall()
    db.close()
    return rows


def get_posts_by_user(username):
    db = sqlite3.connect("database.db", check_same_thread=False)
    rows = db.execute("""
        SELECT posts.id, posts.title, posts.content, posts.image_path, posts.theme, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE users.username = ?
        ORDER BY posts.created_at DESC
    """, (username,)).fetchall()
    db.close()
    return rows


def add_post(user_id, title, content, theme, image_path=None):
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute(
        "INSERT INTO posts (user_id, title, content, image_path, theme) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, content, image_path, theme)
    )
    db.commit()
    db.close()


def delete_post(post_id, user_id):
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute(
        "DELETE FROM posts WHERE id = ? AND user_id = ?",
        (post_id, user_id)
    )
    db.commit()
    db.close()
''', encoding="utf-8")

pathlib.Path('database/comments.py').write_text(
'''import sqlite3


def get_comments():
    db = sqlite3.connect("database.db", check_same_thread=False)
    rows = db.execute("""
        SELECT comments.post_id, comments.content, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.created_at
    """).fetchall()
    db.close()
    return rows


def get_comments_by_user_posts(username):
    db = sqlite3.connect("database.db", check_same_thread=False)
    rows = db.execute("""
        SELECT comments.post_id, comments.content, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id IN (
            SELECT id FROM posts WHERE user_id = (SELECT id FROM users WHERE username = ?)
        )
        ORDER BY comments.created_at
    """, (username,)).fetchall()
    db.close()
    return rows


def add_comment(post_id, user_id, content):
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute(
        "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
        (post_id, user_id, content)
    )
    db.commit()
    db.close()
''', encoding="utf-8")

pathlib.Path('database/categories.py').write_text(
'''import sqlite3


def get_visit_count():
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime(\'now\'))")
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    db.close()
    return count


THEMES = [
    "opiskelu",
    "vapaa-aika",
    "musiikki",
    "elokuvat/sarjat",
    "urheilu",
    "lukeminen",
    "pelit",
]
''', encoding="utf-8")

pathlib.Path('database/post_categories.py').write_text(
'''import sqlite3


def init_db():
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
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "blog_name" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN blog_name TEXT")
    db.commit()
    db.close()
''', encoding="utf-8")

pathlib.Path('database/__init__.py').write_text('', encoding="utf-8")

print("Kaikki tiedostot kirjoitettu!")
