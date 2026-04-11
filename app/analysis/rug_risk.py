def calculate_risk(liquidity, lock_status):

    score = 0

    if liquidity < 1:
        score += 2

    if lock_status == "UNLOCKED":
        score += 3

    if score <= 2:
        return "LOW"

    if score <= 4:
        return "MEDIUM"

    return "HIGH"