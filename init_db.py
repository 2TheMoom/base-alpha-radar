import sqlite3

conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_address TEXT UNIQUE,
    name TEXT,
    symbol TEXT,
    supply TEXT,
    deployer TEXT,
    block INTEGER,
    is_token INTEGER
)
""")

conn.commit()
conn.close()

print("Database initialized with correct schema.")