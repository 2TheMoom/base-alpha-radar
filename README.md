# Base Alpha Radar

Base Alpha Radar is an open on-chain intelligence engine that tracks new tokens, liquidity events, and emerging activity on the Base network in near real time.

The goal of this project is to create an open analytics layer for discovering new tokens, stealth launches, and ecosystem signals before they appear on traditional dashboards.

---

# Vision

Base Alpha Radar aims to become a public intelligence layer for the Base ecosystem by providing open data on:

- new token deployments
- liquidity creation
- deployer activity
- stealth launches
- smart money behavior

This project is designed to support both **builders and traders** by providing early signals directly from on-chain activity.

---

# Features

Current capabilities include:

- Detect newly deployed ERC-20 tokens
- Detect NFT mint events
- Detect liquidity activity on major Base DEXs
- Track contract deployments
- Near-real-time block scanning
- Event-driven architecture for scalable detectors

Upcoming features:

- 🚨 Stealth launch detection  
- 💧 New liquidity pair detection  
- 🐳 Whale wallet tracking  
- 🔥 Early token discovery signals  
- Dashboard integration with Olumi

---

# Architecture

Base Alpha Radar follows a modular event-driven architecture:

Scanner Layer
↓
Event Queue Layer
↓
Processing Layer
↓
Storage / Alert Layer


### Scanner Layer
Continuously scans new blocks on Base and extracts on-chain events such as:

- token deployments
- mint events
- liquidity activity

### Event Queue Layer
Acts as a buffer between the scanner and detectors, allowing multiple analytics modules to process events in parallel.

### Processing Layer
Runs detection algorithms such as:

- stealth launch detection
- liquidity pattern detection
- whale activity detection

### Storage / Alert Layer
Stores insights and powers dashboards, alerts, and APIs.

---

# Project Structure
base-alpha-radar/
│
├── app/
│ ├── scanner.py # Blockchain event scanner
│ ├── server.py # API server
│ ├── status.py # Health/status endpoint
│ │
│ └── events/
│ └── event_queue.py
│
├── detectors/
│ └── stealth_launch.py # Launch pattern detector (coming next)
│
├── init_db.py
├── contracts.db
├── last_block.txt
│
├── check_tokens.py
├── check_db.py
│
└── README.md

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

# Roadmap

Short-term roadmap:

1. Event Queue Layer  
2. Stealth Launch Detector  
3. Liquidity Pair Detection  
4. Whale Wallet Tracking  
5. Alpha Dashboard

Long-term vision:

Base Alpha Radar becomes an open **Base ecosystem intelligence platform** that powers:

- token discovery
- trading signals
- developer analytics
- ecosystem dashboards

---

# License

MIT License