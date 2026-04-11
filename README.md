# Base Alpha Radar

Base Alpha Radar is a real-time token launch scanner for the Base network.

It monitors decentralized exchange factory contracts and detects newly tradable tokens as soon as liquidity pools are created.

The tool extracts critical trading intelligence such as liquidity size, deployer wallet, early buyer activity, and rug-risk signals.

---

## Features

### Token Launch Detection

Detects newly created trading pairs on supported DEXs.

### Liquidity Analysis

Reads pair reserves and filters pools below the minimum liquidity threshold.

### Base Token Filtering

Only tracks pairs against major Base assets:

* WETH
* USDC
* USDbC

### Deployer Detection

Identifies the wallet that created the launch transaction.

### Early Buyer Tracking

Tracks the first buyer and first five buys after launch.

### Liquidity Lock Detection

Identifies whether LP tokens are locked or remain in deployer control.

### Rug Risk Signals

Evaluates launch safety using indicators such as:

* deployer supply concentration
* unlocked liquidity
* small liquidity pools
* suspicious deployer behavior

---

## Example Output

🚨 NEW TRADABLE TOKEN DETECTED

Time: 2026-04-11 03:44:30

Token: X1000XLiquidBGT (LIQUIDBGT)
Contract: 0xed93Cbfcd61bA8398ACce99Db7b9aaAaee7cc08e

DEX: Uniswap V2
Pair Address: 0x8e90F88860d9bc1c5127baF5C4620A14959390e8

Base Token: WETH
Liquidity: 1.53 WETH

Creator: 0xa2f8FfA445505f9CdE3d335227e6f11f69018188

Liquidity Status: UNLOCKED ⚠️
Deployer Supply: 32%

🔥 FIRST BUY DETECTED

Buyer: 0x91e...
Spent: 1.2 WETH

⚡ BUY #2
Buyer: 0x3ac...

⚡ BUY #3
Buyer: 0x88b...

Rug Risk Score: MEDIUM

---

## Architecture

Base Alpha Radar uses an event-driven scanning architecture.

Workflow:

1. The scanner monitors new blocks through an HTTP RPC connection.
2. It listens for `PairCreated` events emitted by supported DEX factory contracts.
3. When a pair is created, token and pair addresses are extracted.
4. Pools are filtered to include only major base token pairs.
5. Pair contracts are queried to read liquidity reserves.
6. Token metadata and deployer information are fetched.
7. Launch intelligence is printed in real time.

Future versions extend the system with swap monitoring, holder analysis, and automated alerts.

---

## Requirements

Python 3.10+

Install dependencies:

pip install web3 python-dotenv

---

## Environment Setup

Create a `.env` file:

BASE_RPC=https://your-base-rpc-url

---

## Running the Scanner

python -m app.scanner.dex_listener

The scanner will start monitoring new blocks and printing launch signals.

---

## Configuration

DEX factories are configured in:

app/config/dex_factories.py

You can add additional DEX factory addresses there.

---

## Minimum Liquidity Filter

Default minimum liquidity:

1 WETH

This value can be adjusted in the scanner configuration.

---

## Current Version

v0.1 — Pair + Liquidity Detection

---

## Roadmap

v0.2
First buy detection and early buyer tracking

v0.3
Liquidity lock detection

v0.4
Holder distribution analysis

v0.5
Telegram alert bot

v0.6
Mempool liquidity detection

v0.7
Smart wallet tracking

---

## Disclaimer

This software is provided for research and educational purposes.

Trading newly launched tokens is extremely risky. Always perform your own due diligence.
