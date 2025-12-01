import sqlite3
import os

# Initialize database
db_path = 'memory/maang_data.db'
schema_path = 'memory/sqlite_schema.sql'

conn = sqlite3.connect(db_path)

with open(schema_path, 'r') as f:
    schema = f.read()
    conn.executescript(schema)

conn.commit()
conn.close()

print('✅ Database initialized successfully!')
print(f'Database created at: {os.path.abspath(db_path)}')
