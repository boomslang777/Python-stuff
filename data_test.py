from dhanhq import dhanhq
import pandas as pd
import time

dhan = dhanhq("9884383177","eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzAzMzAyNzMxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDY0MDMxNyJ9.NvMY4rM-gyiy-gmLeh_7HYPknSxhv4sJ9OPPM8IzPBJQTLvd--8eKG4GA0HsC5Gu2tBQVYVPAqyc1qUFggpfHQ")
while True:
    data = dhan.intraday_daily_minute_charts(
    security_id='40940',
    exchange_segment='NSE_FNO',
    instrument_type='OPTIDX'
    )
    print(data)
    intraday_data = None
    # intraday_data = pd.DataFrame(data['data'])
    # temp_list = []
    # for i in intraday_data['start_Time']:
    #     temp = dhan.convert_to_date_time(i)
    #     temp_list.append(temp)
    # intraday_data['date']  = temp_list
    # intraday_data.set_index('date', inplace=True)
    # print(intraday_data['close'].iloc[-1])
    time.sleep(60)
