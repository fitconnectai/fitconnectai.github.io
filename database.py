import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'fitness.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            google_id TEXT PRIMARY KEY,
            email TEXT,
            name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            google_id TEXT PRIMARY KEY,
            basic TEXT,
            goal TEXT,
            diet TEXT,
            activity TEXT,
            experience TEXT,
            days TEXT,
            health TEXT,
            plan_text TEXT,
            FOREIGN KEY (google_id) REFERENCES users (google_id)
        )
    ''')
    conn.commit()
    conn.close()

def get_profile(google_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM profiles WHERE google_id = ?', (google_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_profile(google_id, metrics, plan_text=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO profiles 
        (google_id, basic, goal, diet, activity, experience, days, health, plan_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (google_id, metrics.get('basic'), metrics.get('goal'), metrics.get('diet'),
          metrics.get('activity'), metrics.get('experience'), metrics.get('days'),
          metrics.get('health'), plan_text))
    conn.commit()
    conn.close()

def save_user(google_id, email, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO users (google_id, email, name)
        VALUES (?, ?, ?)
    ''', (google_id, email, name))
    conn.commit()
    conn.close()
