import sqlite3


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
