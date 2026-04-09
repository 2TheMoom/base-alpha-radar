from web3 import Web3

# Major DEX factories on Base

DEX_FACTORIES = {

    "aerodrome": Web3.to_checksum_address(
        "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"
    ),

    "uniswap_v2": Web3.to_checksum_address(
        "0x8909Dc15e40173fF4699343b6eB8132c65e18eC6"
    ),

    "baseswap": Web3.to_checksum_address(
        "0xFDa619b6d2090fEdcB52cC1eA8E4E59C0f7dF7C3"
    ),

    "alienbase": Web3.to_checksum_address(
        "0x9C4ec768c28520B50860ea7a15bd7213a9fF58bf"
    )

}