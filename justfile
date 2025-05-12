# Download ETH futures kline data
download-eth-futures:
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    python python/download-kline.py -s ETHUSDT -t spot -y 2024 -i 5m -folder ~/Developer/crypto-backtest/data -c 1 -skip-daily 1

# Create and activate virtual environment
venv:
    python3 -m venv .venv
    @echo "Virtual environment created. Activate it with:"
    @echo "source .venv/bin/activate"

# Install dependencies
install:
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    pip install -r python/requirements.txt

# Default recipe to run when just is called without arguments
default:
    @just --list