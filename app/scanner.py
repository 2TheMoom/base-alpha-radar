import os
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get RPC URL from .env file
RPC_URL = os.getenv("BASE_RPC_URL")

if not RPC_URL:
    print("❌ BASE_RPC_URL not found in .env file")
    exit()

# Connect to Base network
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ Failed to connect to Base")
    exit()

print("✅ Connected to Base")

# Function to scan a block
def scan_block(block_number):
    try:
        block = w3.eth.get_block(block_number, full_transactions=True)

        print(f"\n🔎 Scanning block {block_number}")
        print(f"Transactions in block: {len(block.transactions)}")

        for tx in block.transactions:

            # Detect contract deployment
            if tx.to is None:
                print("🚀 Possible contract deployment:", tx.hash.hex())

    except Exception as e:
        print("Block scan error:", e)


# Main scanner loop
def start_scanner():
    latest_block = w3.eth.block_number
    print("Starting scanner from block:", latest_block)

    while True:
        try:
            current_block = w3.eth.block_number

            if current_block >= latest_block:

                for block_number in range(latest_block, current_block + 1):
                    scan_block(block_number)

                latest_block = current_block + 1

            time.sleep(5)

        except Exception as e:
            print("Scanner error:", e)
            time.sleep(5)


# Start scanner
start_scanner()