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

# -----------------------------
# EVENT SIGNATURES
# -----------------------------
TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()
APPROVAL_TOPIC = w3.keccak(text="Approval(address,address,uint256)").hex()
PAIR_CREATED_TOPIC = w3.keccak(text="PairCreated(address,address,address,uint256)").hex()

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# -----------------------------
# FACTORY CONTRACTS
# -----------------------------
UNISWAP_FACTORY = w3.to_checksum_address("0x8909Dc15e40173ff4699343b6eb8132c65e18ec6")

AERODROME_FACTORY = w3.to_checksum_address("0x420dd381b31aef6683db6b902084cb0ffece40da")

BASESWAP_FACTORY = w3.to_checksum_address("0xFDa619b6d209f8F0a7d2E0C7E57b7d3d0C9C1a90")

FACTORIES = {
    "Uniswap": UNISWAP_FACTORY,
    "Aerodrome": AERODROME_FACTORY,
    "BaseSwap": BASESWAP_FACTORY
}

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
            # CONTRACT DEPLOYMENTS
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
            # MINT EVENTS
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

                except Exception:
                    pass

            # -----------------------------
            # APPROVAL EVENTS
            # -----------------------------
            approval_logs = w3.eth.get_logs({
                "fromBlock": current_block,
                "toBlock": current_block,
                "topics": [APPROVAL_TOPIC]
            })

            for log in approval_logs:

                try:

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

                    print("\n⚡ Approval Event Detected")
                    print(f"Name: {name}")
                    print(f"Symbol: {symbol}")
                    print(f"Contract: {token_address}")
                    print(f"Supply: {total_supply}")
                    print(f"Block: {current_block}")
                    print(f"Time: {block_time}")
                    print("---------------------")

                except Exception:
                    pass

            # -----------------------------
            # LIQUIDITY PAIR CREATION
            # -----------------------------
            for dex_name, factory_address in FACTORIES.items():

                try:

                    pair_logs = w3.eth.get_logs({
                        "address": factory_address,
                        "fromBlock": current_block,
                        "toBlock": current_block,
                        "topics": [PAIR_CREATED_TOPIC]
                    })

                    print(f"{dex_name} liquidity events found: {len(pair_logs)}")

                    for log in pair_logs:

                        token0 = "0x" + log["topics"][1].hex()[-40:]
                        token1 = "0x" + log["topics"][2].hex()[-40:]

                        print("\n💧 Liquidity Pair Created")
                        print(f"DEX: {dex_name}")
                        print(f"Token A: {token0}")
                        print(f"Token B: {token1}")
                        print(f"Block: {current_block}")
                        print(f"Time: {block_time}")
                        print("---------------------")

                except Exception:
                    pass

            save_last_block(current_block)

            current_block += 1

        time.sleep(3)

    except Exception as e:

        print("Scanner error:", e)
        time.sleep(5)