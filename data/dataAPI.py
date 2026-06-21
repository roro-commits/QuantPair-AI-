import os
import yfinance as yf
from quantpairs.reusableModule.reusable_module import drop_columns
from quantpairs.reusableModule.reusable_module import rename_column
import pandas as pd

# import panda as df
# 


os.makedirs('data',exist_ok=True)

tickers = ['MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'ADBE', 'AMD', 'QCOM', '^GSPC', '^VIX']



data = yf.download(tickers, start='2018-01-01', end='2025-12-31', auto_adjust=True)


def download_data (tickers:list, start_date:str, end_date: str, auto_adjust: bool  ) -> None:
    """
    A function to donwnload daily stock data from Yahoo finance:
    Index : Date 
    OPEN
    HIGH
    LOW
    CLOSE
    TICKER
    """

    for tick in tickers:
        data = yf.download(tick, start=start_date, end=end_date, auto_adjust=auto_adjust)
        fname = tick.replace('^', '')
        data.columns = data.columns.droplevel('Ticker')   # strip redundant header level
        data.index.name = 'Date'
        data['Ticker'] = fname           
        data.to_csv(f'data/{fname}.csv')






def close_data(data_frame: pd.DataFrame,column: list[str]):
    
    data_frame = drop_columns(data_frame, column)
    keys = data_frame.columns.values
    print ("keys %s %s", keys, data_frame.iloc[0]['Ticker'])
    col_new_name =  data_frame.iloc[0]['Ticker']+"-"+keys[0]
    data_frame = rename_column(data_frame,"Close", col_new_name)
    data_frame = drop_columns(data_frame, keys[1])
    print("result %s", data_frame)

    return data_frame

def master_data(data_frame: pd.DataFrame,column: list[str]) -> None:
    """"
    A function to create  a master data to use for analysis
    
      Per Stock:
        - Close price
		- Daily return — (Xₜ − Xₜ₋₁)/Xₜ₋₁ × 100
		
		**Market context (shared across all):**
		
		- S&P 500 daily return
		- VIX
		
		**Calendar indicators:**
		- Year
		- Quarter
		- Month
		
		**Index:**
		- Date (one row per trading day)
    """
    close_frames = []
    
    closed_data = close_data(data_frame, column)
    close_frames.append(closed_data)

    print("all closed frames %s", close_frames)


    
def main():

    download_data(tickers,'2018-01-01', '2025-12-31',True)
    drop_column =["High","Low","Open","Volume"]
    
    try:
     df = pd.read_csv("data/AAPL.csv", index_col="Date")
     master_data(df, drop_column)
    except FileNotFoundError as fnf:
     print(" %s", fnf)

if __name__== "__main__":
    main()
