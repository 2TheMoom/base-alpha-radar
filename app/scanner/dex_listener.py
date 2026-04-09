import os
import time
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

from app.config.dex_factories import DEX_FACTORIES

load_dotenv()

RPC_URL = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 30}))

if not w3.is_connected():
    print("Failed to connect to Base RPC")
    exit()

print("Connected to Base RPC")


# -------------------------------------------------
# BASE TOKENS WE CARE ABOUT
# -------------------------------------------------

WETH = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")

USDC = Web3.to_checksum_address("0xd9aAEc86B65D86f6A7B5A7F9F1FfE9A2c1b9C2eA")

VALID_BASE_TOKENS = {WETH, USDC}


# -------------------------------------------------
# EVENT SIGNATURES
# -------------------------------------------------

PAIR_CREATED_TOPIC = w3.keccak(
    text="PairCreated(address,address,address,uint256)"
).hex()

MINT_TOPIC = w3.keccak(
    text="Mint(address,uint256,uint256)"
).hex()

SWAP_TOPIC = w3.keccak(
    text="Swap(address,uint256,uint256,uint256,uint256,address)"
).hex()


# -------------------------------------------------
# TRACKED POOLS
# -------------------------------------------------

tracked_pools = {}


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def topic_to_address(topic):
    return Web3.to_checksum_address("0x" + topic.hex()[-40:])


def extract_pair_address(data):

    hex_data = data.hex()

    pair = "0x" + hex_data[26:66]

    return Web3.to_checksum_address(pair)


def get_token_metadata(token):

    abi = [
        {
            "name": "name",
            "outputs": [{"type": "string"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "name": "symbol",
            "outputs": [{"type": "string"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    try:

        contract = w3.eth.contract(address=token, abi=abi)

        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()

        return name, symbol

    except:
        return None, None


# -------------------------------------------------
# HANDLE NEW PAIR
# -------------------------------------------------

def handle_pair_created(log):

    token0 = topic_to_address(log["topics"][1])
    token1 = topic_to_address(log["topics"][2])

    pair = extract_pair_address(log["data"])

    if token0 not in VALID_BASE_TOKENS and token1 not in VALID_BASE_TOKENS:
        return

    name0, sym0 = get_token_metadata(token0)
    name1, sym1 = get_token_metadata(token1)

    print("\n🚨 NEW TRADABLE TOKEN DETECTED")
    print("Time:", now())
    print("Token0:", name0, sym0)
    print("Token1:", name1, sym1)
    print("Pair:", pair)

    tracked_pools[pair] = {
        "token0": token0,
        "token1": token1,
        "liquidity": False,
        "first_buy": False,
    }


# -------------------------------------------------
# LIQUIDITY DETECTION
# -------------------------------------------------

def detect_liquidity(pair):

    if tracked_pools[pair]["liquidity"]:
        return

    print("\n💧 LIQUIDITY ADDED")
    print("Pair:", pair)

    tracked_pools[pair]["liquidity"] = True


# -------------------------------------------------
# FIRST BUY DETECTION
# -------------------------------------------------

def detect_first_buy(pair):

    if tracked_pools[pair]["first_buy"]:
        return

    print("\n🐳 FIRST BUY DETECTED")
    print("Pair:", pair)

    tracked_pools[pair]["first_buy"] = True


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def main():

    print("Starting Base Alpha Radar")

    pair_filter = w3.eth.filter({
        "address": list(DEX_FACTORIES.values()),
        "topics": [PAIR_CREATED_TOPIC]
    })

    while True:

        try:

            logs = pair_filter.get_new_entries()

            for log in logs:
                handle_pair_created(log)

            for pair in list(tracked_pools.keys()):

                pool_filter = w3.eth.filter({
                    "address": pair
                })

                pool_logs = pool_filter.get_new_entries()

                for log in pool_logs:

                    topic = log["topics"][0].hex()

                    if topic == MINT_TOPIC:
                        detect_liquidity(pair)

                    elif topic == SWAP_TOPIC:
                        detect_first_buy(pair)

            time.sleep(2)

        except Exception as e:

            print("Radar error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()