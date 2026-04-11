import os
import time
from datetime import datetime

from web3 import Web3
from dotenv import load_dotenv

from app.config.dex_factories import DEX_FACTORIES


load_dotenv()

RPC = os.getenv("BASE_RPC")

w3 = Web3(Web3.HTTPProvider(RPC))

if not w3.is_connected():
    print("Failed to connect to RPC")
    exit()

print("Connected to Base HTTP RPC")
print("Starting Base Alpha Radar")
print("Scanning blocks...")


BASE_TOKENS = {
    Web3.to_checksum_address("0x4200000000000000000000000000000000000006"): "WETH",
    Web3.to_checksum_address("0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"): "USDC",
    Web3.to_checksum_address("0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca"): "USDbC",
}


PAIR_CREATED_TOPIC = w3.keccak(
    text="PairCreated(address,address,address,uint256)"
).hex()


MIN_LIQUIDITY = 1 * 10**18   # 1 WETH minimum


def get_token_info(token):

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

    contract = w3.eth.contract(address=token, abi=abi)

    try:
        name = contract.functions.name().call()
    except:
        name = "Unknown"

    try:
        symbol = contract.functions.symbol().call()
    except:
        symbol = "UNK"

    return name, symbol


def get_liquidity(pair):

    abi = [
        {
            "name": "getReserves",
            "outputs": [
                {"type": "uint112"},
                {"type": "uint112"},
                {"type": "uint32"},
            ],
            "inputs": [],
            "stateMutability": "view",
            "type": "function",
        }
    ]

    try:
        contract = w3.eth.contract(address=pair, abi=abi)

        reserves = contract.functions.getReserves().call()

        return reserves

    except:
        return None


def main():

    last_block = w3.eth.block_number

    while True:

        latest_block = w3.eth.block_number

        if latest_block > last_block:

            logs = w3.eth.get_logs({
                "fromBlock": last_block,
                "toBlock": latest_block,
                "address": list(DEX_FACTORIES.values()),
                "topics": [PAIR_CREATED_TOPIC],
            })

            for log in logs:

                token0 = Web3.to_checksum_address(
                    "0x" + log["topics"][1].hex()[-40:]
                )

                token1 = Web3.to_checksum_address(
                    "0x" + log["topics"][2].hex()[-40:]
                )

                if token0 not in BASE_TOKENS and token1 not in BASE_TOKENS:
                    continue


                pair = Web3.to_checksum_address(
                    "0x" + log["data"].hex()[24:64]
                )


                base_token = token0 if token0 in BASE_TOKENS else token1
                token = token1 if token0 in BASE_TOKENS else token0


                name, symbol = get_token_info(token)


                reserves = get_liquidity(pair)

                if reserves:

                    reserve0, reserve1, _ = reserves

                    liquidity = reserve0 if token0 in BASE_TOKENS else reserve1

                    if liquidity < MIN_LIQUIDITY:
                        continue

                    liquidity_eth = liquidity / 10**18

                else:
                    liquidity_eth = 0


                tx = w3.eth.get_transaction(log["transactionHash"])
                creator = tx["from"]


                dex_name = "Unknown"

                for dex, addr in DEX_FACTORIES.items():

                    if addr.lower() == log["address"].lower():

                        dex_name = dex
                        break


                print("\n🚨 NEW TRADABLE TOKEN DETECTED\n")

                print("Time:", datetime.utcnow())
                print("Token:", name, f"({symbol})")
                print("Contract:", token)

                print("DEX:", dex_name)

                print("Pair Address:", pair)

                print("Base Token:", BASE_TOKENS[base_token])

                print("Liquidity:", round(liquidity_eth, 4), BASE_TOKENS[base_token])

                print("Creator:", creator)

                print("\n🔥 ALPHA SIGNAL\n")


            last_block = latest_block


        time.sleep(3)


if __name__ == "__main__":
    main()