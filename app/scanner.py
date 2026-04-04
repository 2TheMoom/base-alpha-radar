import os
import time
import sqlite3
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ Failed to connect")
    exit()

print("✅ Connected to Base")

# DATABASE
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_number INTEGER,
    contract_address TEXT,
    deployer TEXT,
    token_name TEXT,
    token_symbol TEXT
)
""")

conn.commit()

latest_block = w3.eth.block_number

while True:
    try:

        block = w3.eth.get_block(latest_block, full_transactions=True)

        print(f"🔎 Scanning Block {latest_block}")

        for tx in block.transactions:

            if tx["to"] is None:

                receipt = w3.eth.get_transaction_receipt(tx["hash"])
                contract_address = receipt.contractAddress
                deployer = tx["from"]

                token_name = None
                token_symbol = None

                try:
                    contract = w3.eth.contract(
                        address=contract_address,
                        abi=[
                            {"name": "name", "outputs":[{"type":"string"}],"inputs":[],"stateMutability":"view","type":"function"},
                            {"name": "symbol","outputs":[{"type":"string"}],"inputs":[],"stateMutability":"view","type":"function"}
                        ]
                    )

                    token_name = contract.functions.name().call()
                    token_symbol = contract.functions.symbol().call()

                    print("🪙 TOKEN DETECTED")
                    print(token_name, token_symbol)

                except:
                    pass

                cursor.execute("""
                INSERT INTO contracts
                (block_number, contract_address, deployer, token_name, token_symbol)
                VALUES (?, ?, ?, ?, ?)
                """, (latest_block, contract_address, deployer, token_name, token_symbol))

                conn.commit()

        latest_block += 1

    except Exception as e:

        time.sleep(2)