import sqlite3
import time
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("BASE_RPC_URL")

if RPC_URL is None:
    raise Exception("BASE_RPC_URL not found in .env")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("Failed to connect to Base RPC")

print("Connected to Base")

# -------------------
# DATABASE
# -------------------

conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT UNIQUE,
    deployer TEXT,
    block INTEGER,
    is_token INTEGER,
    name TEXT,
    symbol TEXT,
    supply TEXT
)
""")

conn.commit()

# -------------------
# ERC20 ABI
# -------------------

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]


def get_token_data(address):
    try:
        contract = w3.eth.contract(address=address, abi=ERC20_ABI)

        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        supply = contract.functions.totalSupply().call()

        return 1, name, symbol, str(supply)

    except:
        return 0, None, None, None


# -------------------
# HISTORICAL SCAN
# -------------------

latest_block = w3.eth.block_number
start_block = latest_block - 1000

print(f"Scanning historical blocks {start_block} → {latest_block}")

for block_number in range(start_block, latest_block + 1):

    block = w3.eth.get_block(block_number, full_transactions=True)

    for tx in block.transactions:

        if tx.to is None:

            receipt = w3.eth.get_transaction_receipt(tx.hash)

            contract_address = receipt.contractAddress
            deployer = tx["from"]

            is_token, name, symbol, supply = get_token_data(contract_address)

            print(
                f"Contract | {contract_address} | Token {is_token} | {symbol}"
            )

            try:
                cursor.execute("""
                INSERT INTO contracts
                (address, deployer, block, is_token, name, symbol, supply)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_address,
                    deployer,
                    block_number,
                    is_token,
                    name,
                    symbol,
                    supply
                ))

                conn.commit()

            except sqlite3.IntegrityError:
                pass

print("Historical scan complete")
print("Switching to live monitoring")

# -------------------
# LIVE SCANNER
# -------------------

current_block = latest_block + 1

while True:

    latest_block = w3.eth.block_number

    while current_block <= latest_block:

        block = w3.eth.get_block(current_block, full_transactions=True)

        for tx in block.transactions:

            if tx.to is None:

                receipt = w3.eth.get_transaction_receipt(tx.hash)

                contract_address = receipt.contractAddress
                deployer = tx["from"]

                is_token, name, symbol, supply = get_token_data(contract_address)

                print(
                    f"NEW | {contract_address} | Token {is_token} | {symbol}"
                )

                try:
                    cursor.execute("""
                    INSERT INTO contracts
                    (address, deployer, block, is_token, name, symbol, supply)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        contract_address,
                        deployer,
                        current_block,
                        is_token,
                        name,
                        symbol,
                        supply
                    ))

                    conn.commit()

                except sqlite3.IntegrityError:
                    pass

        current_block += 1

    time.sleep(5)