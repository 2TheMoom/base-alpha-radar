from app.events.event_queue import get_events

# simple memory store
recent_events = {}


def run_detector():

    events = get_events()

    for event in events:

        contract = event.get("contract")

        if contract is None:
            continue

        if contract not in recent_events:
            recent_events[contract] = {
                "deploy": False,
                "mint": False,
                "liquidity": False,
                "symbol": None,
                "block": None,
                "timestamp": None
            }

        record = recent_events[contract]

        if event["type"] == "deploy":
            record["deploy"] = True

        if event["type"] == "token_mint":
            record["mint"] = True
            record["symbol"] = event.get("symbol")
            record["block"] = event.get("block")
            record["timestamp"] = event.get("timestamp")

        if event["type"] == "liquidity":
            record["liquidity"] = True

        # stealth launch detected
        if record["deploy"] and record["mint"] and record["liquidity"]:

            print("\n🚨 STEALTH LAUNCH DETECTED\n")

            print("Token:", record["symbol"])
            print("Contract:", contract)
            print("Block:", record["block"])
            print("Time:", record["timestamp"])

            print("\nSequence:")
            print("✔ Deploy")
            print("✔ Mint")
            print("✔ Liquidity")

            print("\n----------------------------------\n")

            # prevent duplicate alerts
            recent_events.pop(contract)