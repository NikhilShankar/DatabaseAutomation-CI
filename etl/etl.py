import pandas as pd
import pymysql
import time
import os
from datetime import datetime
import numpy as np

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 4408)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpass'),
    'database': os.getenv('DB_NAME', 'nyc311')
}

CHUNK_SIZE = 10000
CSV_FILE = 'data/data_311_Jan_2025.csv'

def clean_data(df):
    """Clean and transform the data"""
    # Fix missing boroughs - handle if column exists
    if 'Borough' in df.columns:
        df['Borough'] = df['Borough'].fillna('UNKNOWN').replace('', 'UNKNOWN')

    # Handle dates - convert to datetime, invalid dates become NaT (NULL in SQL)
    if 'Created Date' in df.columns:
        df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    if 'Closed Date' in df.columns:
        df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')

    # Handle missing coordinates
    if 'Latitude' in df.columns:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    if 'Longitude' in df.columns:
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # Replace NaN with None for proper NULL handling in MySQL
    df = df.replace({np.nan: None})

    return df

def safe_value(val):
    """Convert pandas NaN/NaT to Python None for MySQL"""
    if pd.isna(val):
        return None
    return val

def main():
    print("Starting ETL process...")
    start_time = time.time()

    # Connect to database
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    total_rows = 0
    chunk_num = 0
    error_count = 0

    try:
        # First, peek at the CSV to see column names
        sample_df = pd.read_csv(CSV_FILE, nrows=1)
        print(f"CSV Columns: {list(sample_df.columns)}")
        print()

        # Read CSV in chunks
        for chunk in pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE):
            chunk_num += 1
            print(f"Processing chunk {chunk_num} ({len(chunk)} rows)...")

            # Clean the data
            chunk = clean_data(chunk)

            # Insert data (idempotent with REPLACE)
            for _, row in chunk.iterrows():
                try:
                    cursor.execute("""
                        REPLACE INTO service_requests
                        (unique_key, created_date, closed_date, agency, complaint_type,
                         descriptor, borough, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        safe_value(row.get('Unique Key')),
                        safe_value(row.get('Created Date')),
                        safe_value(row.get('Closed Date')),
                        safe_value(row.get('Agency')),
                        safe_value(row.get('Complaint Type')),
                        safe_value(row.get('Descriptor')),
                        safe_value(row.get('Borough', 'UNKNOWN')),
                        safe_value(row.get('Latitude')),
                        safe_value(row.get('Longitude'))
                    ))
                except Exception as e:
                    error_count += 1
                    if error_count <= 10:  # Only print first 10 errors
                        print(f"Error inserting row {safe_value(row.get('Unique Key'))}: {e}")
                    continue

            conn.commit()
            total_rows += len(chunk)
            print(f"  Inserted {len(chunk)} rows (Total: {total_rows})")

        # Calculate statistics
        end_time = time.time()
        duration = end_time - start_time
        rows_per_sec = total_rows / duration if duration > 0 else 0

        print("\n" + "="*50)
        print("ETL COMPLETE - Statistics:")
        print(f"  Total rows processed: {total_rows}")
        print(f"  Errors encountered: {error_count}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Speed: {rows_per_sec:.2f} rows/second")
        print("="*50)

    except Exception as e:
        print(f"Error during ETL: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
