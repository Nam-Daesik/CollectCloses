import pandas as pd
import yfinance as yf
import pandas_market_calendars as mcal
from datetime import datetime
import pytz
import time
import os

# --- 서머타임(DST) 체크 및 대기 로직 ---
# 뉴욕 타임존 기준 현재 시간 확인
ny_tz = pytz.timezone('America/New_York')
ny_time = datetime.now(ny_tz)

# 현재 뉴욕 시간이 서머타임(DST)을 적용받는지 확인 (1이면 서머타임, 0이면 해제)
is_dst = ny_time.dst().seconds != 0

if is_dst:
    print(f"현재 뉴욕은 서머타임 적용 기간입니다. (데이터 즉시 수집 시작: {ny_time})")
else:
    print(f"현재 뉴욕은 서머타임 해제(겨울철) 기간입니다. 1시간 대기 후 수집을 시작합니다... ({ny_time})")
    time.sleep(3600)  # 3600초(1시간) 대기

# ---------------------------------------

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
usdkrw_data = yf.download('KRW=X', period='1d', progress=False)
current_rate = round(float(usdkrw_data['Close'].iloc[-1]), 2)

data.index.name = str(current_rate)

output_filename = os.path.join(base_dir, 'master_regular_close.csv')
data.to_csv(output_filename)

print(f"저장 완료: {output_filename}")
