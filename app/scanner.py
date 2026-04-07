import time
import os
from web3 import Web3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_RPC = os.getenv("BASE_RPC")

w3 = Web3(Web3.HTTPProvider(BASE_RPC))

if not w3.is_connected():
    print("❌ Failed to connect to Base RPC")
    exit()

print("✅ Connected to Base RPC")

TRANSFER_SIG = w3.keccak(text="Transfer(address,address,uint256)").hex()
PAIR_CREATED_SIG = w3.keccak(text="PairCreated(address,address,address,uint256)").hex()

DEX_FACTORIES = [
    Web3.to_checksum_address("0x8909Dc15e40173fF4699343b6eb8132c65e18eC6"),
    Web3.to_checksum_address("0x33128a8fC17869897dcE68Ed026d694621f6FDfD"),
]

ERC20_ABI = [
    {"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"}
]


def get_token_info(contract):

    try:

        token = w3.eth.contract(address=contract, abi=ERC20_ABI)

        decimals = token.functions.decimals().call()

        name = token.functions.name().call()
        symbol = token.functions.symbol().call()
        supply = token.functions.totalSupply().call()

        supply = supply / (10 ** decimals)

        return name, symbol, supply

    except:

        return None


def detect_token_mint(log):

    if log["topics"][0].hex() == TRANSFER_SIG:

        from_addr = "0x" + log["topics"][1].hex()[-40:]
        to_addr = "0x" + log["topics"][2].hex()[-40:]

        if from_addr.lower() == "0x0000000000000000000000000000000000000000":

            contract = Web3.to_checksum_address(log["address"])

            token_info = get_token_info(contract)

            if not token_info:
                return

            name, symbol, supply = token_info

            amount = int(log["data"].hex(), 16) if log["data"] else 0

            print("\n🔥 Token Mint Detected")
            print("Name:", name)
            print("Symbol:", symbol)
            print("Mint Amount:", amount)
            print("Total Supply:", supply)
            print("Contract:", contract)
            print("Minted To:", Web3.to_checksum_address(to_addr))


def detect_pair_creation(log):

    if log["topics"][0].hex() == PAIR_CREATED_SIG:

        factory = log["address"]

        if factory in DEX_FACTORIES:

            token0 = Web3.to_checksum_address("0x" + log["topics"][1].hex()[-40:])
            token1 = Web3.to_checksum_address("0x" + log["topics"][2].hex()[-40:])

            print("\n💧 Liquidity Pair Created")
            print("Factory:", factory)
            print("Token0:", token0)
            print("Token1:", token1)


def detect_contract_deployment(tx):

    if tx["to"] is None:

        receipt = w3.eth.get_transaction_receipt(tx["hash"])

        contract = receipt["contractAddress"]

        if not contract:
            return

        contract = Web3.to_checksum_address(contract)

        token_info = get_token_info(contract)

        if not token_info:
            return

        name, symbol, supply = token_info

        print("\n🚀 Token Deployed")
        print("Name:", name)
        print("Symbol:", symbol)
        print("Total Supply:", supply)
        print("Contract:", contract)
        print("Deployer:", tx["from"])


def scan_block(block_number):

    block = w3.eth.get_block(block_number, full_transactions=True)

    block_time = datetime.fromtimestamp(block.timestamp)

    print(f"\nScanning block {block_number} | {block_time}")

    for tx in block.transactions:

        detect_contract_deployment(tx)

        receipt = w3.eth.get_transaction_receipt(tx.hash)

        for log in receipt.logs:

            detect_token_mint(log)

            detect_pair_creation(log)


def main():

    latest_block = w3.eth.block_number

    start_block = latest_block - 20

    print(f"Starting near latest block: {start_block}")

    current_block = start_block

    while True:

        latest_block = w3.eth.block_number

        if current_block <= latest_block:

            scan_block(current_block)

            current_block += 1

        else:

            time.sleep(2)


if __name__ == "__main__":
    main()