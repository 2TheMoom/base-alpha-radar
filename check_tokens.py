import sqlite3

conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM contracts")

count = cursor.fetchone()[0]

print("Total tokens stored:", count)

conn.close()