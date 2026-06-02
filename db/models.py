import sqlite3 as lite

class DatabaseManager(object):

    def __init__(self):
        self.conn = lite.connect("bd.db")
        self.conn.execute('pragma foreign_keys = ON')
        self.conn.row_factory = lite.Row
        self.conn.commit()
        self.cur = self.conn.cursor()

    def create_tables(self):
        self.query('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER UNIQUE NOT NULL, username TEXT, admin INTEGER DEFAULT 0)')
        self.query('CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id INTEGER NOT NULL, category TEXT NOT NULL, problem TEXT, photo_id TEXT, status TEXT DEFAULT "open", created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (tg_id) REFERENCES users(tg_id))')

    def query(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()
        return self.cur.lastrowid

    def fetchone(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()

db = DatabaseManager()