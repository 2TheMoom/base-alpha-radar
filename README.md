# Base Alpha Radar

Base Alpha Radar is a lightweight on-chain scanner that detects newly tradable tokens on the Base network.

It monitors DEX factories, identifies new trading pairs, and tracks when liquidity is added and the first buy occurs.

---

## Features

- Tracks major Base DEX factories
- Detects new token pairs
- Filters pairs involving WETH and USDC
- Fetches token name and symbol
- Detects liquidity added
- Detects first buy transactions

---

## Architecture

DEX Factory → PairCreated Event

LP Contract Monitoring:
- Mint → Liquidity Added
- Swap → First Buy

---

## Project Structure

base-alpha-radar
 app/
 scanner/
  dex_listener.py

config/
 dex_factories.py

detectors/
 liquidity_detector.py
 stealth_launch.py

events/
 event_queue.py


---

## Run the Radar
 python -m app.scanner.dex_listener
 

 ## Setup

Clone the repository:

```
git clone https://github.com/2TheMoom/base-alpha-radar.git
cd base-alpha-radar
```

Create a virtual environment:

```
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```
pip install web3 flask python-dotenv
```

Create a `.env` file:

```
BASE_RPC_URL=your_base_rpc_endpoint
```

Initialize the database:

```
python init_db.py
```

Run the scanner:

```
python app/scanner.py
```

Run the API server:

```
python app/server.py
```


---

## Current Development

Milestone 1
DEX Factory Scanner ✅

Milestone 2
Liquidity Detection 🚧

Milestone 3
First Buy Detection 🚧

Milestone 4
Liquidity Size Filtering

Milestone 5
Multi-chain Support

---

## Goal

Detect newly tradable tokens on Base in near-real-time.