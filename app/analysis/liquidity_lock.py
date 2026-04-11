from web3 import Web3

DEAD_ADDRESS = Web3.to_checksum_address(
    "0x000000000000000000000000000000000000dEaD"
)

UNICRYPT = Web3.to_checksum_address(
    "0x663A5C229c09b049e36dCc11C18c00C9dB4E6c6F"
)

TEAM_FINANCE = Web3.to_checksum_address(
    "0xE2fE530C047f2d85298b07D9333C05737f1435Fb"
)


def check_liquidity_lock(w3, pair):

    abi = [
        {
            "name": "totalSupply",
            "outputs": [{"type": "uint256"}],
            "inputs": [],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "name": "balanceOf",
            "outputs": [{"type": "uint256"}],
            "inputs": [{"type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    contract = w3.eth.contract(address=pair, abi=abi)

    total_lp = contract.functions.totalSupply().call()

    burned = contract.functions.balanceOf(DEAD_ADDRESS).call()
    unicrypt = contract.functions.balanceOf(UNICRYPT).call()
    team = contract.functions.balanceOf(TEAM_FINANCE).call()

    locked = burned + unicrypt + team

    if locked > 0:
        return "LOCKED"

    return "UNLOCKED"