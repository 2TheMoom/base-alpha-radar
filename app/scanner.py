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
NFT_APPROVAL_TOPIC = w3.keccak(text="ApprovalForAll(address,address,bool)").hex()


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
        {
            "name": "totalSupply",
            "outputs": [{"type": "uint256"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    try:

        contract = w3.eth.contract(address=token, abi=abi)

        name = contract.functions.name().call()
        symbol = contract.functions.symbol().call()
        supply = contract.functions.totalSupply().call()

        return name, symbol, supply

    except:

        return "Unknown", "Unknown", 0


def detect_token_mint(log, block_time):

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return

    if len(log["topics"]) < 3:
        return

    from_addr = "0x" + log["topics"][1].hex()[-40:]

    if from_addr.lower() != "0x0000000000000000000000000000000000000000":
        return

    token = log["address"]

    data = log["data"]

    if data in (b"", "0x", None):
        return

    try:
        amount = int(data.hex(), 16) if isinstance(data, bytes) else int(data, 16)
    except:
        return

    name, symbol, supply = get_token_metadata(token)

    print("\n🔥 Token Mint Detected")
    print("Time:", block_time)
    print("Name:", name)
    print("Symbol:", symbol)
    print("Mint Amount:", amount)
    print("Total Supply:", supply)
    print("Contract:", token)


def detect_liquidity(log, block_time):

    if log["topics"][0].hex() != LIQUIDITY_TOPIC:
        return False

    pair = log["address"]

    print("\n💧 Liquidity Added")
    print("Time:", block_time)
    print("Pool:", pair)

    return True


def detect_nft_approval(log, block_time):

    if log["topics"][0].hex() != NFT_APPROVAL_TOPIC:
        return

    owner = "0x" + log["topics"][1].hex()[-40:]
    operator = "0x" + log["topics"][2].hex()[-40:]

    print("\n🟣 Contract Approval Detected")
    print("Time:", block_time)
    print("Owner:", owner)
    print("Operator:", operator)
    print("Contract:", log["address"])


def scan_block(block_number):

    block = w3.eth.get_block(block_number)

    timestamp = datetime.utcfromtimestamp(block["timestamp"])

    print(f"\nScanning block {block_number} | {timestamp}")

    try:

        logs = w3.eth.get_logs(
            {
                "fromBlock": block_number,
                "toBlock": block_number,
            }
        )

    except Exception as e:

        print("Log fetch error:", e)
        return

    liquidity_count = 0

    for log in logs:

        detect_token_mint(log, timestamp)

        if detect_liquidity(log, timestamp):
            liquidity_count += 1

        detect_nft_approval(log, timestamp)

    print("\n📊 Liquidity Summary")
    print("Block:", block_number)
    print("Liquidity Events:", liquidity_count)


def main():

    latest_block = w3.eth.block_number

    current_block = latest_block - 1

    print("Starting near latest block:", current_block)

    while True:

        latest_block = w3.eth.block_number

        if current_block <= latest_block:

            scan_block(current_block)

            current_block += 1

        else:

            time.sleep(1)


if __name__ == "__main__":
    main()