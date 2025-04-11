import sqlite3
import hashlib
from typing import Optional, Tuple

DATABASE_NAME = "users.db"

def initialize_database():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def create_user(username: str, password: str, email: Optional[str] = None) -> bool:
    """Create a new user in the database."""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username or email already exists
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials."""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        return cursor.fetchone() is not None
    finally:
        conn.close()

def get_user(username: str) -> Optional[Tuple]:
    """Get user details."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT username, email, created_at FROM users WHERE username = ?",
            (username,)
        )
        
        return cursor.fetchone()
    finally:
        conn.close()

def show_all_users():
    """Print all users in tabular format."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users")
    rows = cursor.fetchall()

    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Created At'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2] or '':<30} {row[3]}")
    conn.close()

# Call this to display the table
show_all_users()

# Initialize the database when this module is imported
initialize_database()      