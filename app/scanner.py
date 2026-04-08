import os
import sys
import time
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.events.event_queue import push_event
from detectors.stealth_launch import run_detector


load_dotenv()

RPC = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC))

print("Connected to Base RPC")


TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()
APPROVAL_TOPIC = w3.keccak(text="Approval(address,address,uint256)").hex()


def get_timestamp(block):

    ts = block["timestamp"]

    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def detect_token_mint(log, timestamp, block_number):

    if len(log["topics"]) == 0:
        return False

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return False

    if len(log["topics"]) < 3:
        return False

    from_addr = "0x" + log["topics"][1].hex()[-40:]

    if from_addr != "0x0000000000000000000000000000000000000000":
        return False

    contract = log["address"]

    try:
        amount = int(log["data"], 16)
    except:
        amount = 0

    event_data = {
        "contract": contract,
        "amount": amount,
        "block": block_number,
        "timestamp": timestamp
    }

    push_event("mint", event_data)

    return True


def detect_contract_deploy(tx, receipt, timestamp, block_number):

    if receipt["contractAddress"] is None:
        return False

    contract = receipt["contractAddress"]

    event_data = {
        "contract": contract,
        "block": block_number,
        "timestamp": timestamp
    }

    push_event("deploy", event_data)

    return True


def detect_liquidity_event(log, timestamp, block_number):

    if len(log["topics"]) == 0:
        return False

    topic = log["topics"][0].hex()

    # simple heuristic detection
    if "swap" in topic.lower():

        event_data = {
            "dex": "DEX",
            "block": block_number,
            "timestamp": timestamp
        }

        push_event("liquidity", event_data)

        return True

    return False


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

                    detect_token_mint(log, timestamp, block_number)

                    detect_liquidity_event(log, timestamp, block_number)

            except Exception:
                continue

    except Exception as e:

        print("Block scan error:", e)


def get_last_block():

    if not os.path.exists("last_block.txt"):
        return w3.eth.block_number - 1

    with open("last_block.txt", "r") as f:
        return int(f.read().strip())


def save_last_block(block):

    with open("last_block.txt", "w") as f:
        f.write(str(block))


def main():

    last_block = get_last_block()

    while True:

        try:

            latest_block = w3.eth.block_number

            if latest_block > last_block:

                for block in range(last_block + 1, latest_block + 1):

                    scan_block(block)

                    last_block = block

                    save_last_block(last_block)

            # Run detectors on queued events
            run_detector()

            time.sleep(1)

        except Exception as e:

            print("Scanner error:", e)

            time.sleep(5)


if __name__ == "__main__":
    main()