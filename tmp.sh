# Activate virtual environment if it exists and run python script
# Usage: just download-spot-kline ETHUSDT BTCUSDT [other symbols...]
download-spot-kline symbols...:
    #!/usr/bin/env bash
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    python3 python/download-kline.py -t spot -s {{symbols}}

# Download ETH/USDT and BTC/USDT
just download-spot-kline ETHUSDT BTCUSDT

# Download SOL/USDT only
just download-spot-kline SOLUSDT

# Download multiple other pairs
just download-spot-kline ADAUSDT XRPUSDT DOTUSDT