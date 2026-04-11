import sqlite3
from datetime import datetime

DB_NAME = "radar.db"


def init_db():

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS launches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_name TEXT,
        token_symbol TEXT,
        token_address TEXT,
        pair_address TEXT,
        dex TEXT,
        base_token TEXT,
        liquidity REAL,
        creator TEXT,
        liquidity_locked TEXT,
        rug_risk TEXT,
        detected_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS buys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_address TEXT,
        buyer TEXT,
        amount REAL,
        buy_number INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_launch(data):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO launches (
        token_name,
        token_symbol,
        token_address,
        pair_address,
        dex,
        base_token,
        liquidity,
        creator,
        liquidity_locked,
        rug_risk,
        detected_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()