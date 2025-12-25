import sqlite3

DB_NAME = "whisper_chat.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        gender TEXT,
        age INTEGER,
        nsfw_allowed INTEGER DEFAULT 0,
        reports INTEGER DEFAULT 0,
        banned INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def upsert_user(user_id, gender=None, age=None, nsfw_allowed=None):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (user_id, gender, age, nsfw_allowed)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        gender = COALESCE(?, gender),
        age = COALESCE(?, age),
        nsfw_allowed = COALESCE(?, nsfw_allowed)
    """, (
        user_id, gender, age, nsfw_allowed,
        gender, age, nsfw_allowed
    ))

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id": row[0],
        "gender": row[1],
        "age": row[2],
        "nsfw_allowed": bool(row[3]),
        "reports": row[4],
        "banned": bool(row[5])
    }

def add_report(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET reports = reports + 1
    WHERE user_id=?
    """, (user_id,))

    conn.commit()
    conn.close()
