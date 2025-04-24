# Activate virtual environment if it exists and run python script
# Usage: just download-spot-kline ETHUSDT BTCUSDT [other symbols...]
download-spot-kline symbols:
    #!/usr/bin/env bash
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    python3 python/download-kline.py -t spot -s {{symbols}}

# Process downloaded data (unzip and concatenate)
process-data:
    #!/usr/bin/env bash
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    python3 python/process_data.py 