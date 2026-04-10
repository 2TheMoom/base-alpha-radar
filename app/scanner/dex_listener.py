import os
import time
from datetime import datetime

from web3 import Web3
from dotenv import load_dotenv

from app.config.dex_factories import DEX_FACTORIES


load_dotenv()

RPC = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.LegacyWebSocketProvider(RPC))

print("Connected to Base WebSocket RPC")
print("Starting Base Alpha Radar")


# Base tokens
WETH = Web3.to_checksum_address(
    "0x4200000000000000000000000000000000000006"
)

USDC = Web3.to_checksum_address(
    "0xd9aAEc86B65D86f6A7B5A7F9F1FfE9A2c1b9C2eA"
)

VALID_BASE = {WETH, USDC}


# Event signatures
PAIR_CREATED = w3.keccak(
    text="PairCreated(address,address,address,uint256)"
).hex()

MINT = w3.keccak(
    text="Mint(address,uint256,uint256)"
).hex()

SWAP = w3.keccak(
    text="Swap(address,uint256,uint256,uint256,uint256,address)"
).hex()


tracked_pairs = {}


def now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def topic_to_address(topic):

    return Web3.to_checksum_address(
        "0x" + topic.hex()[-40:]
    )


def extract_pair(data):

    raw = data.hex()

    pair = "0x" + raw[26:66]

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

        return "Unknown", "UNK"


def detect_pair(log):

    token0 = topic_to_address(log["topics"][1])
    token1 = topic_to_address(log["topics"][2])

    pair = extract_pair(log["data"])

    factory = log["address"]

    dex = "Unknown"

    for name, addr in DEX_FACTORIES.items():

        if addr.lower() == factory.lower():

            dex = name


    if token0 in VALID_BASE:

        base = token0
        token = token1

    elif token1 in VALID_BASE:

        base = token1
        token = token0

    else:

        return


    name, symbol = get_token_metadata(token)

    creator = w3.eth.get_transaction(
        log["transactionHash"]
    )["from"]


    tracked_pairs[pair] = {

        "token": token,
        "name": name,
        "symbol": symbol,
        "base": base,
        "dex": dex,
        "creator": creator,
        "liquidity": 0,
        "first_buy": False,

    }


def detect_liquidity(pair, log):

    tx = w3.eth.get_transaction(
        log["transactionHash"]
    )

    eth_value = w3.from_wei(tx["value"], "ether")

    if eth_value == 0:

        return


    tracked_pairs[pair]["liquidity"] = eth_value

    data = tracked_pairs[pair]

    base_symbol = "WETH" if data["base"] == WETH else "USDC"


    print("\n🚨 NEW TOKEN LAUNCH\n")

    print("Time:", now())
    print()

    print("Token:", data["name"], f"({data['symbol']})")
    print("Contract:", data["token"])
    print()

    print("DEX:", data["dex"])
    print()

    print("Base Pair:", base_symbol)
    print("Pair Address:", pair)
    print()

    print("Creator Wallet:", data["creator"])
    print()

    print("Liquidity Added:", eth_value, base_symbol)


def detect_swap(pair):

    data = tracked_pairs[pair]

    if data["first_buy"]:

        return

    if data["liquidity"] == 0:

        return


    print()
    print("First Buy Detected")
    print()
    print("🔥 ALPHA SIGNAL 🔥")
    print()


    tracked_pairs[pair]["first_buy"] = True


def main():

    pair_filter = w3.eth.filter({

        "address": list(DEX_FACTORIES.values()),
        "topics": [PAIR_CREATED],

    })


    print("Listening for new pools...\n")


    while True:

        try:

            logs = pair_filter.get_new_entries()

            for log in logs:

                detect_pair(log)


            for pair in list(tracked_pairs.keys()):

                pool_filter = w3.eth.filter({

                    "address": pair

                })


                pool_logs = pool_filter.get_new_entries()

                for log in pool_logs:

                    topic = log["topics"][0].hex()

                    if topic == MINT:

                        detect_liquidity(pair, log)

                    elif topic == SWAP:

                        detect_swap(pair)


            time.sleep(2)

        except Exception as e:

            print("Radar error:", e)

            time.sleep(5)


if __name__ == "__main__":

    main()