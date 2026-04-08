import time
from web3 import Web3
from datetime import datetime

RPC_URL = "https://mainnet.base.org"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

print("Connected to Base RPC")

TRANSFER_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

DEX_ROUTERS = {
    "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86": "Uniswap",
    "0xcF77a3Ba9A5CA399B7c97c74d54e5b1b9E36FfC9": "Aerodrome"
}


def safe_rpc(fn):
    try:
        return fn()
    except:
        return None


def get_token_metadata(address):

    abi = [
        {"constant":True,"inputs":[],"name":"name","outputs":[{"type":"string"}],"type":"function"},
        {"constant":True,"inputs":[],"name":"symbol","outputs":[{"type":"string"}],"type":"function"},
        {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"type":"uint256"}],"type":"function"}
    ]

    try:

        contract = w3.eth.contract(address=address, abi=abi)

        name = safe_rpc(lambda: contract.functions.name().call())
        symbol = safe_rpc(lambda: contract.functions.symbol().call())
        supply = safe_rpc(lambda: contract.functions.totalSupply().call())

        return name or "Unknown", symbol or "Unknown", supply or 0

    except:
        return "Unknown","Unknown",0


def detect_token_mint(log, timestamp):

    if "topics" not in log:
        return False

    if len(log["topics"]) == 0:
        return False

    if log["topics"][0].hex() != TRANSFER_TOPIC:
        return False

    if len(log["topics"]) < 3:
        return False

    from_addr = "0x" + log["topics"][1].hex()[-40:]

    if from_addr.lower() != ZERO_ADDRESS:
        return False

    token = log["address"]

    name, symbol, supply = get_token_metadata(token)

    # ---------- NFT MINT ----------
    if len(log["topics"]) == 4:

        try:
            token_id = int(log["topics"][3].hex(), 16)
        except:
            token_id = 0

        print("\n🖼 NFT Mint Detected")
        print("Time:", timestamp)
        print("Name:", name)
        print("Symbol:", symbol)
        print("Token ID:", token_id)
        print("Contract:", token)

        return True


    # ---------- ERC20 MINT ----------
    amount = 0

    try:
        if log["data"] != "0x":
            amount = int(log["data"], 16)
    except:
        amount = 0

    print("\n🔥 Token Mint Detected")
    print("Time:", timestamp)
    print("Name:", name)
    print("Symbol:", symbol)
    print("Mint Amount:", amount)
    print("Total Supply:", supply)
    print("Contract:", token)

    return True


def detect_liquidity(tx, timestamp):

    if tx["to"] is None:
        return False

    if tx["to"].lower() not in [x.lower() for x in DEX_ROUTERS]:
        return False

    dex = DEX_ROUTERS[tx["to"]]

    print("\n💧 Liquidity Event")
    print("Time:", timestamp)
    print("DEX:", dex)
    print("Tx:", tx["hash"].hex())

    return True


def detect_contract_deploy(receipt, timestamp):

    if receipt["contractAddress"] is None:
        return False

    contract = receipt["contractAddress"]

    name, symbol, supply = get_token_metadata(contract)

    if name == "Unknown" and symbol == "Unknown":
        return False

    print("\n🚀 Token Deployed")
    print("Time:", timestamp)
    print("Name:", name)
    print("Symbol:", symbol)
    print("Total Supply:", supply)
    print("Contract:", contract)

    return True


def scan_block(block_number):

    block = safe_rpc(lambda: w3.eth.get_block(block_number, full_transactions=True))

    if block is None:
        return

    timestamp = datetime.utcfromtimestamp(block["timestamp"])

    print(f"\nScanning block {block_number} | {timestamp}")

    mint_count = 0
    deploy_count = 0
    liquidity_count = 0

    for tx in block["transactions"]:

        receipt = safe_rpc(lambda: w3.eth.get_transaction_receipt(tx["hash"]))

        if receipt is None:
            continue

        if detect_contract_deploy(receipt, timestamp):
            deploy_count += 1

        if detect_liquidity(tx, timestamp):
            liquidity_count += 1

        for log in receipt["logs"]:

            try:

                if detect_token_mint(log, timestamp):
                    mint_count += 1

            except:
                continue

    print("\n📊 Block Summary")
    print("Token Minted:", mint_count)
    print("Token Deployed:", deploy_count)
    print("Liquidity Events:", liquidity_count)


def main():

    last_block = w3.eth.block_number - 1

    while True:

        try:

            latest_block = w3.eth.block_number

            if latest_block > last_block:

                for block in range(last_block + 1, latest_block + 1):

                    scan_block(block)

                last_block = latest_block

        except:
            pass

        time.sleep(1)


if __name__ == "__main__":
    main()