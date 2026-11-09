import sqlite3

connection = sqlite3.connect("dreams.db")

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS dreams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    text TEXT,
    mood TEXT,
    theme TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

try:
    cursor.execute("ALTER TABLE dreams ADD COLUMN user_id INTEGER")
except sqlite3.OperationalError:
    pass
connection.commit()
connection.close()

print("Database created successfully!")