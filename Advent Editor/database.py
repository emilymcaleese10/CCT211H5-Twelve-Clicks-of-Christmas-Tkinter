import sqlite3
from config import DB_FILE, DOOR_DATES

class SqliteRepo:
    """Handles all DB operations cleanly."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.ensure_db()

    def ensure_db(self):
        c = self.conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS viewer (
                id INTEGER PRIMARY KEY,
                name TEXT
            )""")

        c.execute("""
            CREATE TABLE IF NOT EXISTS door (
                id INTEGER PRIMARY KEY,
                door_num INTEGER UNIQUE,
                date_day INTEGER,
                message TEXT,
                image_path TEXT
            )""")

        c.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )""")

        for i, day in enumerate(DOOR_DATES, start=1):
            c.execute("""
                INSERT OR IGNORE INTO door(door_num, date_day, message, image_path)
                VALUES (?, ?, ?, ?)""",
                (i, day, None, None))

        self.conn.commit()

    def set_viewer_name(self, name: str):
        c = self.conn.cursor()
        c.execute("DELETE FROM viewer")
        c.execute("INSERT INTO viewer(name) VALUES (?)", (name,))
        self.conn.commit()

    def get_door(self, door_num: int):
        c = self.conn.cursor()
        c.execute("SELECT message, image_path FROM door WHERE door_num = ?", (door_num,))
        return c.fetchone()

    def update_door(self, door_num: int, message: str, img_path: str):
        c = self.conn.cursor()
        c.execute("""
            UPDATE door
            SET message = ?, image_path = ?
            WHERE door_num = ?""",
            (message, img_path, door_num))
        self.conn.commit()

    def close(self):
        self.conn.close()
