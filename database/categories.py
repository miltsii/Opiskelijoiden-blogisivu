import sqlite3


def get_visit_count():
    db = sqlite3.connect("database.db", check_same_thread=False)
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
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
