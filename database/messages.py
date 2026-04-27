import sqlite3


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
