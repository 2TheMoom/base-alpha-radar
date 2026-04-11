def analyze_distribution(w3, token):

    try:

        holders = w3.eth.get_logs({
            "fromBlock": 0,
            "toBlock": "latest",
            "address": token
        })

        holder_count = len(holders)

        if holder_count < 20:
            return "HIGH CONCENTRATION"

        if holder_count < 50:
            return "MEDIUM"

        return "GOOD DISTRIBUTION"

    except:
        return "UNKNOWN"