import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    phone = "0725806332"
    raw_password = "12345"
    password_hash = pwd_context.hash(raw_password)

    try:
        cursor.execute("""
            INSERT INTO admins (phone_number, password_hash)
            VALUES (?, ?)
        """, (phone, password_hash))
        conn.commit()
        print(f"Successfully created admin account for phone: {phone}")
    except sqlite3.IntegrityError:
        print(f"Admin account with phone {phone} already exists.")
    
    conn.close()

if __name__ == "__main__":
    seed_admin()