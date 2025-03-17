import os
import pandas as pd 
import configparser 
from datetime import datetime, timedelta
from yfinance import download

from pgdb import PGDatabase

config = configparser.ConfigParser()
config.read('config.ini')

COMPANIES = eval(config['Companies']['COMPANIES'])
SALES_PATH = config['Files']['SALES_PATH']
DATABASE_CREDS = config['Database']

sales_df = pd.DataFrame()
if os.path.exists(SALES_PATH):
    sales_df = pd.read_csv(SALES_PATH)
    # os.remove(SALES_PATH)
    

historical_d = {}

for company in COMPANIES:
    historical_d[company] = download(
        tickers=company, 
        start=(datetime.today() - timedelta(days=5)).strftime('%Y-%m-%d'), 
        end=(datetime.today() - timedelta(days=4)).strftime('%Y-%m-%d')
    )

for i, data in historical_d.items():
    for j, row in data.iterrows():
        print(row.iloc[3])
        print('000000000000000')
    print('----------------')


database = PGDatabase(
    host=DATABASE_CREDS['HOST'], 
    database=DATABASE_CREDS['DATABASE'], 
    user=DATABASE_CREDS['USER'], 
    password=DATABASE_CREDS['PASSWORD'], 
)

for i, row in sales_df.iterrows():
    query = f"insert into sales values ('{row['dt']}', '{row['company']}', '{row['transaction_type']}', '{row['amount']}')"
    database.post(query)

for company, data in historical_d.items():
    for i, row in data.iterrows():
        query = f"insert into stock values ('{row.name.date()}', '{row.reset_index()['Ticker'].unique()[0]}', '{row.iloc[3]}', '{row.iloc[0]}')"
        database.post(query)
