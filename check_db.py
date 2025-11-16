import sqlite3

conn = sqlite3.connect('memory/interview.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

print("Database tables:")
for table in tables:
    print(f"  - {table}")

conn.close()
