import os
import time
import sqlite3
from datetime import datetime, timezone
from web3 import Web3
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()
RPC_URL = os.getenv("BASE_RPC_URL")

# -----------------------------
# CONNECT WEB3
# -----------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Failed to connect to RPC")
    exit()

print("Connected to Base RPC")

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()

# -----------------------------
# ERC20 ABI
# -----------------------------
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "type": "function",
    },
]

# ERC20 Transfer Event Signature
TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()

# Zero address used for mint detection
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# -----------------------------
# LAST BLOCK TRACKING
# -----------------------------
LAST_BLOCK_FILE = "last_block.txt"


def get_last_block():
    if os.path.exists(LAST_BLOCK_FILE):
        with open(LAST_BLOCK_FILE, "r") as f:
            return int(f.read().strip())
    return w3.eth.block_number


def save_last_block(block):
    with open(LAST_BLOCK_FILE, "w") as f:
        f.write(str(block))


current_block = get_last_block()

print(f"Starting scan from block {current_block}")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    try:

        latest_block = w3.eth.block_number

        while current_block <= latest_block:

            print(f"Scanning block {current_block}")

            block = w3.eth.get_block(current_block, full_transactions=True)

            block_time = datetime.fromtimestamp(
                block.timestamp, timezone.utc
            )

            # -----------------------------
            # CHECK CONTRACT DEPLOYMENTS
            # -----------------------------
            for tx in block.transactions:

                try:

                    receipt = w3.eth.get_transaction_receipt(tx.hash)

                    contract_address = receipt.contractAddress

                    if contract_address:

                        try:

                            token = w3.eth.contract(
                                address=contract_address,
                                abi=ERC20_ABI
                            )

                            name = token.functions.name().call()
                            symbol = token.functions.symbol().call()
                            total_supply = token.functions.totalSupply().call()

                            deployer = tx["from"]

                            print("\n🚀 New Token (Deployment)")
                            print(f"Name: {name}")
                            print(f"Symbol: {symbol}")
                            print(f"Contract: {contract_address}")
                            print(f"Deployer: {deployer}")
                            print(f"Supply: {total_supply}")
                            print(f"Block: {current_block}")
                            print(f"Time: {block_time}")
                            print("---------------------")

                            cursor.execute(
                                """
                                INSERT OR IGNORE INTO contracts
                                (contract_address, name, symbol, total_supply, block_number)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (
                                    contract_address,
                                    name,
                                    symbol,
                                    total_supply,
                                    current_block,
                                ),
                            )

                            conn.commit()

                        except Exception:
                            pass

                except Exception:
                    pass

            # -----------------------------
            # CHECK ERC20 MINT EVENTS
            # -----------------------------
            logs = w3.eth.get_logs({
                "fromBlock": current_block,
                "toBlock": current_block,
                "topics": [TRANSFER_TOPIC]
            })

            for log in logs:

                try:

                    from_address = "0x" + log["topics"][1].hex()[-40:]

                    if from_address.lower() == ZERO_ADDRESS.lower():

                        token_address = log["address"]

                        token = w3.eth.contract(
                            address=token_address,
                            abi=ERC20_ABI
                        )

                        try:
                            name = token.functions.name().call()
                            symbol = token.functions.symbol().call()
                            total_supply = token.functions.totalSupply().call()
                        except Exception:
                            continue

                        print("\n🔥 Token Mint Detected")
                        print(f"Name: {name}")
                        print(f"Symbol: {symbol}")
                        print(f"Contract: {token_address}")
                        print(f"Supply: {total_supply}")
                        print(f"Block: {current_block}")
                        print(f"Time: {block_time}")
                        print("---------------------")

                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO contracts
                            (contract_address, name, symbol, total_supply, block_number)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                token_address,
                                name,
                                symbol,
                                total_supply,
                                current_block,
                            ),
                        )

                        conn.commit()

                except Exception:
                    pass

            save_last_block(current_block)

            current_block += 1

        time.sleep(3)

    except Exception as e:

        print("Scanner error:", e)
        time.sleep(5)