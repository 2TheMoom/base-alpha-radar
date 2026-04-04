import os
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RPC_URL = os.getenv("BASE_RPC_URL")

# Connect to Base
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ Failed to connect to Base")
    exit()

print("✅ Connected to Base")

latest_block = w3.eth.block_number
print(f"Starting from block: {latest_block}")

while True:
    try:
        block = w3.eth.get_block(latest_block, full_transactions=True)

        print(f"\n🔎 Scanning Block: {latest_block}")

        for tx in block.transactions:

            # Contract creation transaction
            if tx["to"] is None:

                contract_address = w3.eth.get_transaction_receipt(tx["hash"]).contractAddress
                deployer = tx["from"]

                print("🚀 New Contract Detected")
                print(f"Deployer: {deployer}")
                print(f"Contract: {contract_address}")
                print("-" * 40)

        latest_block += 1

    except Exception as e:
        print("Waiting for next block...")
        time.sleep(2)