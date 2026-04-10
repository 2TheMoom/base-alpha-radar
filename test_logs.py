from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

RPC = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.LegacyWebSocketProvider(RPC))

print("Connected:", w3.is_connected())

latest = w3.eth.block_number

print("Latest block:", latest)

block = w3.eth.get_block(latest)

print("Transactions in block:", len(block.transactions))