import sqlite3
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
