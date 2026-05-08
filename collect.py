import pandas as pd
import yfinance as yf
import pandas_market_calendars as mcal
from datetime import datetime
import pytz
import time
import os

ny_tz = pytz.timezone('America/New_York')
ny_time = datetime.now(ny_tz)
is_dst = ny_time.dst().seconds != 0

if not is_dst:
    time.sleep(3600)

base_dir = os.path.dirname(os.path.abspath(__file__))
tickers = ['QQQ', 'TQQQ', 'SOXL', 'TECL', 'SGOV']

df_list = []
for ticker in tickers:
    for attempt in range(3):
        try:
            temp_data = yf.download(ticker, period="max", auto_adjust=False, ignore_tz=True)['Close']
            if not temp_data.empty:
                temp_data.name = ticker
                df_list.append(temp_data)
                break
        except:
            time.sleep(5)
    else:
        raise Exception(f"{ticker} 데이터 수집 3회 실패. 작업을 중단합니다.")

data = pd.concat(df_list, axis=1)

data = data.loc['2010-01-01':]
data = data.ffill().round(2)
data.index = pd.to_datetime(data.index).normalize()
data.dropna(how='all', inplace=True)
data = data[tickers]

if data.isnull().any().any():
    raise ValueError("결측치가 포함된 데이터가 있습니다. 파일 저장을 취소합니다.")

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

usdkrw_data = yf.download('KRW=X', period='1d', progress=False)
current_rate = round(float(usdkrw_data['Close'].iloc[-1]), 2)

data.index.name = str(current_rate)

output_filename = os.path.join(base_dir, 'master_regular_close.csv')
data.to_csv(output_filename)
