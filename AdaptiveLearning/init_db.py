from cs50 import SQL
from werkzeug.security import generate_password_hash

def init_database():
    db = SQL("sqlite:///platform.db")
    
    # Drop existing table if it exists
    db.execute("DROP TABLE IF EXISTS users")
    
    # Create fresh table
    db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            email TEXT UNIQUE,
            reset_token TEXT,
            reset_expires DATETIME
        )
    """)
    
    # Optionally add a test user
    db.execute(
        "INSERT INTO users (username, hash) VALUES (?, ?)",
        "admin", generate_password_hash("password")
    )
    
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()