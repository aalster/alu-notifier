import sqlite3

DB_FILE = "alu_notifier.db"

def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS settings (
                         key   varchar(100) primary key,
                         value varchar(255)
                     );
                     """)