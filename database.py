import sqlite3

dbname = "bd.db"

def init_db():
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            status TEXT DEFAULT 'Открыта',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_ticket(user_id: int,
                  username: str,
                  category: str,
                  problem: str):

    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tickets
        (user_id, username, category, problem)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, category, problem))

    ticket_id = cur.lastrowid

    conn.commit()
    conn.close()

    return ticket_id


def get_user_tickets(user_id: int):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, category, status, created_at
        FROM tickets
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    tickets = cur.fetchall()

    conn.close()

    return tickets