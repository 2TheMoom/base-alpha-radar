# Base Alpha Radar

Base Alpha Radar is an open analytics engine that tracks new token deployments, liquidity events, and early on-chain signals on the Base network.

The goal of this project is to create an open data layer for discovering new tokens and emerging activity on Base in real time.

## Features

- Detect newly deployed ERC-20 tokens on Base
- Track contract deployments
- Store token metadata (name, symbol, supply)
- Lightweight SQLite database
- Fast block-scanner architecture
- Simple API endpoints for querying data

## Project Structure

```
base-alpha-radar/
│
├── app/
│   ├── scanner.py        # Blockchain scanner
│   ├── server.py         # API server
│   └── status.py         # Health/status endpoint
│
├── init_db.py            # Database initialization
├── contracts.db          # SQLite database
├── last_block.txt        # Scanner progress tracker
├── check_tokens.py       # Debug utility
├── check_db.py           # DB inspection
└── README.md
```

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

## Vision

Base Alpha Radar aims to become a public intelligence layer for the Base ecosystem by providing open data on:

- new tokens
- liquidity creation
- deployer activity
- emerging protocols

## License

MIT License