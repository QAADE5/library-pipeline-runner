"""Load silver CSVs into SQL Server - run after the pipeline."""
import pyodbc
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import urllib

SERVER = 'localhost'
DATABASE = 'library_warehouse'
SILVER_DIR = Path('data/silver')

# Create database if it doesn't exist
conn_str = (f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SERVER};DATABASE=master;Trusted_Connection=yes;')
with pyodbc.connect(conn_str, autocommit=True) as conn:
    conn.execute(
        f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{DATABASE}') "
        f"CREATE DATABASE [{DATABASE}]"
    )

# Connect to the warehouse
params = urllib.parse.quote_plus(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
)
engine = create_engine(f'mssql+pyodbc:///?odbc_connect={params}')

# Load each silver CSV - replace overwrites if already there
for csv_file in sorted(SILVER_DIR.glob('*.csv')):
    df = pd.read_csv(csv_file)
    df.to_sql(csv_file.stem, engine, if_exists='replace', index=False)
    print(f'  {csv_file.stem}: {len(df):,} rows loaded')

print(f'\nOpen SSMS > connect to {SERVER} > {DATABASE}')
