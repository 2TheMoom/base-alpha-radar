import time
from web3 import Web3
from datetime import datetime

RPC_URL = "https://mainnet.base.org"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():
    print("✅ Connected to Base RPC")
else:
    print("❌ RPC connection failed")
    exit()

TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()
LIQUIDITY_TOPIC = w3.keccak(text="Mint(address,uint256,uint256)").hex()


def get_token_metadata(address):

    abi = [
        {"name":"name","outputs":[{"type":"string"}],"inputs":[],"stateMutability":"view","type":"function"},
        {"name":"symbol","outputs":[{"type":"string"}],"inputs":[],"stateMutability":"view","type":"function"},
        {"name":"totalSupply","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"}
    ]

    try:

        contract = w3.eth.contract(address=address, abi=abi)

        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        supply = contract.functions.totalSupply().call()

        return name, symbol, supply

    except:

        return "Unknown", "Unknown", 0


def scan_block(block_number):

    block = w3.eth.get_block(block_number, full_transactions=True)

    timestamp = datetime.utcfromtimestamp(block["timestamp"])

    print(f"\nScanning block {block_number} | {timestamp}")

    token_mints = 0
    token_deploys = 0
    liquidity_events = 0
    nft_deploys = 0

    try:

        logs = w3.eth.get_logs({
            "fromBlock": block_number,
            "toBlock": block_number
        })

    except Exception as e:

        print("Log error:", e)
        logs = []

    for log in logs:

        if not log["topics"]:
            continue

        topic = log["topics"][0].hex()

        # TOKEN MINT
        if topic == TRANSFER_TOPIC:

            if len(log["topics"]) < 3:
                continue

            from_addr = "0x" + log["topics"][1].hex()[-40:]

            if from_addr.lower() != "0x0000000000000000000000000000000000000000":
                continue

            data = log["data"]

            if data in (b"", "0x", None):
                continue

            try:
                amount = int(data.hex(),16) if isinstance(data,bytes) else int(data,16)
            except:
                continue

            token = log["address"]

            name,symbol,supply = get_token_metadata(token)

            token_mints += 1

            print("\n🔥 Token Mint Detected")
            print("Name:",name)
            print("Symbol:",symbol)
            print("Mint Amount:",amount)
            print("Total Supply:",supply)
            print("Contract:",token)

        # LIQUIDITY EVENT
        if topic == LIQUIDITY_TOPIC:

            liquidity_events += 1

            print("\n💧 Liquidity Added")
            print("Pool:",log["address"])

    # TOKEN / NFT DEPLOYMENTS
    for tx in block["transactions"]:

        receipt = w3.eth.get_transaction_receipt(tx["hash"])

        if receipt.contractAddress:

            contract = receipt.contractAddress

            name,symbol,supply = get_token_metadata(contract)

            if symbol == "Unknown":

                nft_deploys += 1

                print("\n🖼 NFT Deployed")
                print("Name:",name)
                print("Total Supply:",supply)
                print("Contract:",contract)

            else:

                token_deploys += 1

                print("\n🚀 Token Deployed")
                print("Name:",name)
                print("Symbol:",symbol)
                print("Total Supply:",supply)
                print("Contract:",contract)

    print("\n📊 Block Summary")
    print("Block:",block_number)
    print("Token Minted:",token_mints)
    print("Token Deployed:",token_deploys)
    print("Liquidity Events:",liquidity_events)
    print("NFT Deployed:",nft_deploys)


def main():

    latest_block = w3.eth.block_number

    current_block = latest_block - 1

    print("Starting near latest block:",current_block)

    while True:

        latest_block = w3.eth.block_number

        if current_block <= latest_block:

            scan_block(current_block)

            current_block += 1

        else:

            time.sleep(1)


if __name__ == "__main__":
    main()