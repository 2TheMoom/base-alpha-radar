from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)

# Always locate the database in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "contracts.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------
# Health Check
# ------------------------

@app.route("/")
def status():
    return jsonify({
        "service": "Base Alpha Radar",
        "status": "running"
    })


# ------------------------
# Latest Tokens
# ------------------------

@app.route("/latest-tokens")
def latest_tokens():

    conn = get_db()

    tokens = conn.execute("""
        SELECT name, symbol, supply, deployer, block
        FROM contracts
        WHERE is_token = 1
        ORDER BY block DESC
        LIMIT 25
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in tokens])


# ------------------------
# Top Deployers
# ------------------------

@app.route("/top-deployers")
def top_deployers():

    conn = get_db()

    deployers = conn.execute("""
        SELECT deployer, COUNT(*) as total
        FROM contracts
        GROUP BY deployer
        ORDER BY total DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in deployers])


# ------------------------
# Suspicious Deployers
# ------------------------

@app.route("/suspicious-deployers")
def suspicious_deployers():

    conn = get_db()

    suspicious = conn.execute("""
        SELECT deployer, COUNT(*) as tokens
        FROM contracts
        WHERE is_token = 1
        GROUP BY deployer
        HAVING tokens >= 3
        ORDER BY tokens DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in suspicious])


# ------------------------
# Run Server
# ------------------------

if __name__ == "__main__":
    print("Using database at:", DATABASE)
    app.run(debug=True)