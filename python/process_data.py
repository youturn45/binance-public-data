#!/usr/bin/env python

import os
import zipfile
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def unzip_and_concatenate_data():
    # Get the script's directory
    script_dir = Path(__file__).parent.absolute()
    
    # Base directory for data (relative to script directory)
    base_dir = script_dir / "data"
    
    # Create a temporary directory for unzipped files
    temp_dir = base_dir / "temp_unzipped"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output directory for concatenated files
    output_dir = base_dir / "concatenated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process spot data
    spot_dir = base_dir / "spot"
    if spot_dir.exists():
        process_trading_type(spot_dir, temp_dir, output_dir, "spot")
    else:
        logger.warning(f"Spot directory not found at {spot_dir}")
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    logger.info("Processing completed!")

def process_trading_type(base_dir, temp_dir, output_dir, trading_type):
    # Keep track of processed files to avoid duplicates
    processed_files = set()
    
    # Walk through all directories
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.zip') and not file.endswith('.CHECKSUM'):
                # Skip if we've already processed this file
                if file in processed_files:
                    continue
                
                # Extract symbol and interval from path
                path_parts = Path(root).parts
                if len(path_parts) >= 5:  # Ensure we have enough path components
                    symbol = path_parts[-2]
                    interval = path_parts[-1]
                    
                    # Create output directory structure
                    symbol_output_dir = output_dir / trading_type / symbol / interval
                    symbol_output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Unzip file
                    zip_path = Path(root) / file
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                            logger.info(f"Extracted {file}")
                    except zipfile.BadZipFile:
                        logger.warning(f"Skipping invalid zip file: {zip_path}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing {zip_path}: {str(e)}")
                        continue
                    
                    # Read all CSV files in the unzipped directory
                    dfs = []
                    for csv_file in temp_dir.glob('*.csv'):
                        try:
                            df = pd.read_csv(csv_file)
                            dfs.append(df)
                            logger.info(f"Read CSV file: {csv_file.name}")
                        except Exception as e:
                            logger.error(f"Error reading CSV file {csv_file}: {str(e)}")
                            continue
                    
                    if dfs:
                        try:
                            # Concatenate all DataFrames
                            combined_df = pd.concat(dfs, ignore_index=True)
                            
                            # Sort by timestamp if it exists
                            if 'timestamp' in combined_df.columns:
                                combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'], unit='ms')
                                combined_df = combined_df.sort_values('timestamp')
                            
                            # Save to parquet
                            output_file = symbol_output_dir / f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.parquet"
                            combined_df.to_parquet(output_file, index=False)
                            logger.info(f"Saved concatenated data to {output_file}")
                            
                            # Mark file as processed
                            processed_files.add(file)
                        except Exception as e:
                            logger.error(f"Error processing data for {symbol} {interval}: {str(e)}")
                            continue
                    
                    # Clean up unzipped files
                    for item in temp_dir.glob('*'):
                        if item.is_file():
                            try:
                                item.unlink()
                            except Exception as e:
                                logger.warning(f"Error deleting temporary file {item}: {str(e)}")

if __name__ == "__main__":
    unzip_and_concatenate_data() 