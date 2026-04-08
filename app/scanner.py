import os
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from web3 import Web3
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.events.event_queue import push_event
from detectors.stealth_launch import run_detector

load_dotenv()

RPC = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

print("Connected to Base RPC")

TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()


# -------------------------
# Helper
# -------------------------

def get_timestamp(block):

    ts = block["timestamp"]

    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def get_token_metadata(contract):

    try:

        abi = [
            {"name": "name", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"},
            {"name": "symbol", "outputs": [{"type": "string"}], "inputs": [], "stateMutability": "view", "type": "function"},
            {"name": "totalSupply", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"}
        ]

        token = w3.eth.contract(address=contract, abi=abi)

        name = token.functions.name().call()
        symbol = token.functions.symbol().call()
        supply = token.functions.totalSupply().call()

        return name, symbol, supply

    except:

        return None, None, None


# -------------------------
# Detection
# -------------------------

def detect_mint(log, timestamp, block_number):

    if len(log["topics"]) < 3:
        return

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return

    from_addr = "0x" + log["topics"][1].hex()[-40:]

    if from_addr != "0x0000000000000000000000000000000000000000":
        return

    contract = Web3.to_checksum_address(log["address"])

    if len(log["topics"]) == 3:

        try:
            amount = int(log["data"], 16)
        except:
            amount = 0

        name, symbol, supply = get_token_metadata(contract)

        print("\nToken Mint Detected")
        print("Name:", name)
        print("Symbol:", symbol)
        print("Mint Amount:", amount)
        print("Total Supply:", supply)
        print("Contract:", contract)

        event_data = {
            "type": "token_mint",
            "name": name,
            "symbol": symbol,
            "amount": amount,
            "supply": supply,
            "contract": contract,
            "block": block_number,
            "timestamp": timestamp
        }

        push_event("token_mint", event_data)

    elif len(log["topics"]) == 4:

        token_id = int(log["topics"][3].hex(), 16)

        print("\nNFT Mint Detected")
        print("Token ID:", token_id)
        print("Contract:", contract)

        event_data = {
            "type": "nft_mint",
            "token_id": token_id,
            "contract": contract,
            "block": block_number,
            "timestamp": timestamp
        }

        push_event("nft_mint", event_data)


def detect_contract_deploy(tx, receipt, timestamp, block_number):

    if receipt["contractAddress"] is None:
        return

    contract = receipt["contractAddress"]

    print("\nContract Deployed:", contract)

    event_data = {
        "type": "deploy",
        "contract": contract,
        "block": block_number,
        "timestamp": timestamp
    }

    push_event("deploy", event_data)


# -------------------------
# Block Scanner
# -------------------------

def scan_block(block_number):

    try:

        block = w3.eth.get_block(block_number, full_transactions=True)

        timestamp = get_timestamp(block)

        print(f"\nScanning block {block_number} | {timestamp}")

        for tx in block["transactions"]:

            try:

                receipt = w3.eth.get_transaction_receipt(tx["hash"])

                detect_contract_deploy(tx, receipt, timestamp, block_number)

                for log in receipt["logs"]:

                    detect_mint(log, timestamp, block_number)

            except:
                continue

    except Exception as e:

        print("Block scan error:", e)


# -------------------------
# Progress tracker
# -------------------------

def get_last_block():

    if not os.path.exists("last_block.txt"):
        return None

    with open("last_block.txt", "r") as f:
        return int(f.read().strip())


def save_last_block(block):

    with open("last_block.txt", "w") as f:
        f.write(str(block))


# -------------------------
# Main
# -------------------------

def main():

    last_block = get_last_block()

    latest_block = w3.eth.block_number

    # AUTO SYNC MODE
    if last_block is None:

        print("Starting near latest block")

        last_block = latest_block - 20

    elif latest_block - last_block > 200:

        print("Scanner far behind. Jumping closer to live blocks.")

        last_block = latest_block - 50

    executor = ThreadPoolExecutor(max_workers=6)

    while True:

        try:

            latest_block = w3.eth.block_number

            if latest_block > last_block:

                blocks = list(range(last_block + 1, latest_block + 1))

                executor.map(scan_block, blocks)

                last_block = latest_block

                save_last_block(last_block)

            run_detector()

            time.sleep(0.4)

        except Exception as e:

            print("Scanner error:", e)

            time.sleep(5)


if __name__ == "__main__":
    main()