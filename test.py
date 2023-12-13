
from dhanhq import dhanhq
import pandas as pd
import time
import security_test
import numpy as np
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzAzMzAyNzMxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDY0MDMxNyJ9.NvMY4rM-gyiy-gmLeh_7HYPknSxhv4sJ9OPPM8IzPBJQTLvd--8eKG4GA0HsC5Gu2tBQVYVPAqyc1qUFggpfHQ"
phone = "9884383177"
dhan = dhanhq(phone,token)
print(dhan)
start_time = "09:15:00"
end_time = "15:15:00"

# Define the time interval (15 minutes)
interval = 15 * 60  # 15 minutes in seconds

# Initialize the current time to the start time
# Place an order for Equity Cash
# dhan.place_order(security_id='1333',   #hdfcbank
#     exchange_segment=dhan.NSE,
#     transaction_type=dhan.BUY,
#     quantity=10,
#     order_type=dhan.MARKET,
#     product_type=dhan.INTRA,
#     price=0)
while True:
    # Get the current time
    current_time = time.strftime("%H:%M:%S")
    print(current_time)

    # Check if the current time is within the desired time frame (9:15 am to 11:00 am)
    # if current_time >= start_time and current_time <= end_time :
        # Print the current time for reference
    print(f"Current time: {current_time}")

    data = dhan.intraday_daily_minute_charts(
    security_id='25',
    exchange_segment='IDX_I',
    instrument_type='INDEX'
    )
    print(data)
    if(data['data']):
        intraday_data = pd.DataFrame(data['data'])
    
        temp_list = []
        for i in intraday_data['start_Time']:
            temp = dhan.convert_to_date_time(i)
            temp_list.append(temp)
        intraday_data['date']  = temp_list
        print(intraday_data)  
        a = dhan.get_order_list()
        print(dhan.get_fund_limits())
        print(pd.DataFrame(a['data']))
        intraday_data.set_index('date', inplace=True)

        # Resample to 15-minute bars
        # OHLC stands for Open, High, Low, Close
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }

        # Resample to 15-minute bars
        intraday_data_15M = intraday_data.resample('15T').apply(ohlc_dict)

        # Drop any rows with missing data
        intraday_data_15M.dropna(inplace=True)

        # Reset the index to have 'date' as a column rather than an index
        intraday_data_15M.reset_index(inplace=True)

        # Now you have 'intraday_data_15M' with 15-minute bars OHLC data

        # Continue with your existing code
        a = dhan.get_order_list()
        fund_limits = dhan.get_fund_limits()
        order_list_df = pd.DataFrame(a['data'])

        # Print the 15M data
        print(intraday_data_15M)

        # Print fund limits
        print(fund_limits)

        # Print order list
        print(order_list_df)
        # Calculate candle size (high - low)
        intraday_data_15M['candle_size'] = intraday_data_15M['high'] - intraday_data_15M['low']

        # Calculate candle wick (bear: low, bull: high - close)
        # intraday_data_15M['candle_wick'] = intraday_data_15M['high'] - intraday_data_15M['low'] - abs(intraday_data_15M['close'] - intraday_data_15M['open'])
        # intraday_data_15M['candle_wick'] = intraday_data_15M['open'] - intraday_data_15M['low'] if intraday_data_15M['open'] <= intraday_data_15M['close'] else intraday_data_15M['high'] - intraday_data_15M['close']
        # Calculate the ratio of candle wick to candle size
        intraday_data_15M['candle_wick'] = np.where(intraday_data_15M['open'] <= intraday_data_15M['close'],
                                                intraday_data_15M['high'] - intraday_data_15M['close'],
                                                intraday_data_15M['close'] - intraday_data_15M['low'])
        intraday_data_15M['wick_to_size_ratio'] = intraday_data_15M['candle_wick'] / intraday_data_15M['candle_size']

        # Print the updated DataFrame with candle size, candle wick, and ratio
        print(intraday_data_15M[['date', 'candle_size', 'candle_wick', 'wick_to_size_ratio']])
        import pandas as pd

        # Your code to calculate wick-to-size ratio and have candle data in the DataFrame

        # Create a new column to mark "BUY" or "SELL"
        intraday_data_15M['Signal'] = ""
        last_trade = None

        # Loop through the DataFrame to analyze candles
        for i in range(1, len(intraday_data_15M) - 1):
            # Check if the wick-to-body ratio is greater than 0.8 in the current candle (i)
            if intraday_data_15M.at[i, 'wick_to_size_ratio'] < 0.5:
                # Check if the next candle (i+1) opens near or at the close of the current candle (i)
                # if abs(intraday_data_15M.at[i + 1, 'open'] - intraday_data_15M.at[i, 'close']) <= 50:  # You can adjust the tolerance as needed
                    # Calculate the body size of the current candle (i)
                body_size_i = abs(intraday_data_15M.at[i, 'open'] - intraday_data_15M.at[i, 'close'])
                # Calculate the retracement of the next candle (i+1)
                retracement = abs(intraday_data_15M.at[i + 1, 'low'] - intraday_data_15M.at[i, 'low'])
                # Check if the retracement is not greater than 30% of the body size
                if retracement / body_size_i <= 0.5:
                    # Check if the next candle (i+1) closes higher than its open
                    if intraday_data_15M.at[i + 1, 'close'] > intraday_data_15M.at[i + 1, 'open'] and last_trade != "BUY":
                        intraday_data_15M.at[i + 1, 'Signal'] = "BUY"
                        latest_signal = intraday_data_15M.iloc[-1]['Signal']
                        security_test.fire(latest_signal,intraday_data_15M.iloc[-1]['close'])
                        last_trade = "BUY"
                    elif intraday_data_15M.at[i + 1, 'close'] < intraday_data_15M.at[i + 1, 'open'] and last_trade != "SELL":
                        intraday_data_15M.at[i + 1, 'Signal'] = "SELL"
                        latest_signal = intraday_data_15M.iloc[-1]['Signal']
                        security_test.fire(latest_signal,intraday_data_15M.iloc[-1]['close'])
                        last_trade = "SELL"

                        
                else :
                    intraday_data_15M.at[i + 1, 'Signal'] = "NOPE"   
                
                
    else :
        continue                
                  
                        

    # Display the DataFrame with the "Signal" column
    print(intraday_data_15M[['date', 'candle_size', 'candle_wick', 'wick_to_size_ratio', 'Signal']])
    time.sleep(60)
    if current_time >= end_time :
        security_test.close_positions()
        break
