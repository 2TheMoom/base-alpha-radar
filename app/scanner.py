import os
import sqlite3
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

BASE_RPC = os.getenv("BASE_RPC")

w3 = Web3(Web3.HTTPProvider(BASE_RPC))

if not w3.is_connected():
    raise Exception("Failed to connect to Base RPC")

print("Connected to Base RPC")

# Connect to database
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

# Create contracts table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS contracts (
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


def get_last_scanned_block():
    try:
        with open("last_block.txt", "r") as f:
            return int(f.read().strip())
    except:
        latest = w3.eth.block_number
        return latest - 1000


def save_last_block(block_number):
    with open("last_block.txt", "w") as f:
        f.write(str(block_number))


def get_token_info(address):

    erc20_abi = [
        {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ]

    try:
        contract = w3.eth.contract(address=address, abi=erc20_abi)

        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        supply = contract.functions.totalSupply().call()

        return name, symbol, supply

    except:
        return None


start_block = get_last_scanned_block()
latest_block = w3.eth.block_number

print(f"Starting scan from block {start_block}")
print(f"Latest block {latest_block}")

for block_number in range(start_block, latest_block + 1):

    block = w3.eth.get_block(block_number, full_transactions=True)

    for tx in block.transactions:

        if tx.to is None:

            receipt = w3.eth.get_transaction_receipt(tx.hash)

            contract_address = receipt.contractAddress
            deployer = tx["from"]

            token = get_token_info(contract_address)

            if token:

                name, symbol, supply = token

                print(f"Token found: {name} ({symbol})")

                try:
                    cursor.execute("""
                    INSERT INTO contracts
                    (contract_address, name, symbol, supply, deployer, block, is_token)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        contract_address,
                        name,
                        symbol,
                        str(supply),
                        deployer,
                        block_number,
                        1
                    ))

                    conn.commit()
                    print("Saved to database")

                except sqlite3.IntegrityError:
                    pass

    save_last_block(block_number)

print("Scan complete")