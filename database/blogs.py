import sqlite3


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
