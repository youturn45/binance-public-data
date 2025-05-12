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

# Download data with checksums
download:
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    python python/download-kline.py -s ETHUSDT -t spot -y 2024 2025 -i 5m -c 1 -skip-daily 1 -folder /data

# Verify checksums in a folder
checksum folder=".":
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    echo "Verifying checksums in {{folder}}..."
    find "{{folder}}" -name "*.zip" -type f | while read -r zip_file; do
        checksum_file="${zip_file}.CHECKSUM"
        if [ -f "$checksum_file" ]; then
            echo "Verifying checksum for ${zip_file}"
            (cd "$(dirname "$zip_file")" && shasum -a 256 -c "$(basename "$checksum_file")")
        fi
    done

# Unpack all zip files and convert to parquet files
unpack folder=".":
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    python python/unpack.py "{{folder}}"

# Copy processed data to destination folder while maintaining structure
copy source="." destination="$HOME/Developer/crypto-backtest/data/":
    #!/usr/bin/env bash
    set -e
    . .venv/bin/activate
    # Expand the destination path
    dest_path=$(realpath "{{destination}}")
    echo "Copying processed data from {{source}} to $dest_path..."
    # Create destination if it doesn't exist
    mkdir -p "$dest_path"
    # Find all processed directories
    find "{{source}}" -type d -name "processed" | while read -r processed_dir; do
        # Get the relative path from source
        rel_path=$(realpath --relative-to="{{source}}" "$(dirname "$processed_dir")")
        # Create corresponding directory in destination
        mkdir -p "$dest_path/$rel_path"
        # Copy all parquet files
        find "$processed_dir" -name "*.parquet" -type f | while read -r parquet_file; do
            filename=$(basename "$parquet_file")
            echo "Copying $filename to $dest_path/$rel_path/"
            cp "$parquet_file" "$dest_path/$rel_path/"
        done
    done
    echo "Done copying processed data"

# Default recipe to run when just is called without arguments
default:
    @just --list