import sqlite3
import json
from datetime import datetime

DB_NAME = "health_agent.db"

def init_db():
    """Initialize the database tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table to store user context (Age, Gender, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, gender TEXT)''')
    
    # Table to store past reports (for longitudinal analysis)
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, 
                  upload_date TEXT, raw_data TEXT, risk_score REAL)''')
    conn.commit()
    conn.close()

def save_report(user_id, raw_data, risk_score):
    """Saves a processed report to history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reports (user_id, upload_date, raw_data, risk_score) VALUES (?, ?, ?, ?)",
              (user_id, datetime.now().strftime("%Y-%m-%d"), json.dumps(raw_data), risk_score))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    """Retrieves past reports for context."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT raw_data FROM reports WHERE user_id = ? ORDER BY upload_date DESC LIMIT 5", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

# Initialize on module load
init_db()