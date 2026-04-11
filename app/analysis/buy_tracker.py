from web3 import Web3
import time

# Swap event topic
SWAP_TOPIC = Web3.keccak(text="Swap(address,uint256,uint256,uint256,uint256,address)").hex()


def track_first_buys(w3, pair_address, base_symbol, telegram_alert):

    print("👀 Monitoring buys for pair:", pair_address)

    buy_count = 0
    start_block = w3.eth.block_number

    while buy_count < 5:

        latest_block = w3.eth.block_number

        logs = w3.eth.get_logs({
            "fromBlock": start_block,
            "toBlock": latest_block,
            "address": pair_address,
            "topics": [SWAP_TOPIC]
        })

        for log in logs:

            tx = w3.eth.get_transaction(log["transactionHash"])
            buyer = tx["from"]

            buy_count += 1

            if buy_count == 1:

                message = f"""
🔥 FIRST BUY DETECTED

Buyer: {buyer}

Pair:
{pair_address}
"""

                print(message)
                telegram_alert(message)

            else:

                message = f"""
⚡ BUY #{buy_count}

Buyer: {buyer}
"""

                print(message)
                telegram_alert(message)

            if buy_count >= 5:
                print("✅ First 5 buys tracked\n")
                return

        start_block = latest_block
        time.sleep(2)