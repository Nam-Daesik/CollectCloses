import pandas as pd
import yfinance as yf
import pandas_market_calendars as mcal
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
tickers = ['QQQ', 'SOXX', 'TQQQ', 'SOXL', 'TECL', 'SGOV']

print("데이터 다운로드 중...")
data = yf.download(
    tickers, 
    period="max", 
    auto_adjust=False, 
    ignore_tz=True     
)['Close']

data = data.loc['2010-01-01':]
data = data.ffill().round(2)
data.index = pd.to_datetime(data.index).normalize()
data.dropna(how='all', inplace=True)
data = data[tickers]

nyse = mcal.get_calendar('NYSE')

today = pd.Timestamp.today().normalize()
end_date_for_cal = today + pd.Timedelta(days=100)

valid_days = nyse.valid_days(start_date='2010-01-01', end_date=end_date_for_cal)
valid_days = pd.to_datetime(valid_days).tz_localize(None).normalize()

past_idx = valid_days[valid_days <= today]
future_idx = valid_days[valid_days > today][:50]
full_idx = past_idx.union(future_idx)

data = data.reindex(full_idx)
data.index = data.index.strftime('%Y-%m-%d')
data.index.name = 'Date'

output_filename = os.path.join(base_dir, 'master_regular_close.csv')
data.to_csv(output_filename)

print(f"Done: {output_filename}")