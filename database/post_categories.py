import sqlite3


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
