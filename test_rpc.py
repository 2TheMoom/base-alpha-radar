from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

rpc = os.getenv("BASE_RPC_URL")

w3 = Web3(Web3.HTTPProvider(rpc))

print("Connected:", w3.is_connected())