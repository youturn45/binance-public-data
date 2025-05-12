#!/usr/bin/env python3

import pandas as pd
import glob
import os
import argparse
from pathlib import Path

def process_folder(input_folder):
    """
    Process all zip files in the input folder and its subfolders,
    maintaining the folder structure and merging data in the final subfolder.
    """
    # Convert to Path object for better path handling
    input_path = Path(input_folder)
    
    # Find all zip files recursively
    zip_files = list(input_path.rglob("*.zip"))
    
    if not zip_files:
        print(f"No zip files found in {input_folder}")
        return
    
    print(f"Found {len(zip_files)} zip files to process")
    
    # Process each zip file
    for zip_file in zip_files:
        # Create a temp directory in the same folder as the zip file
        temp_dir = zip_file.parent / "temp_unzip"
        temp_dir.mkdir(exist_ok=True)
        
        print(f"Processing {zip_file.name}...")
        
        # Unzip the file
        os.system(f"unzip -q '{zip_file}' -d '{temp_dir}'")
        
        # Find all CSV files in the temp directory
        csv_files = list(temp_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in {zip_file.name}")
            continue
        
        # Read and combine all CSV files
        dfs = []
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, header=None)
            dfs.append(df)
        
        if dfs:
            # Combine all dataframes
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Create output directory if it doesn't exist
            output_dir = zip_file.parent / "processed"
            output_dir.mkdir(exist_ok=True)
            
            # Save as parquet
            output_file = output_dir / f"{zip_file.stem}.parquet"
            combined_df.to_parquet(output_file, index=False)
            print(f"Created {output_file} with {len(combined_df)} rows")
        
        # Clean up temp directory
        os.system(f"rm -rf '{temp_dir}'")

def main():
    parser = argparse.ArgumentParser(description='Unpack and merge data from zip files')
    parser.add_argument('folder', help='Input folder containing zip files')
    args = parser.parse_args()
    
    process_folder(args.folder)

if __name__ == "__main__":
    main() 