import csv
from datetime import datetime, timedelta
from dhanhq import dhanhq
import time
import pandas as pd
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzAzMzAyNzMxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDY0MDMxNyJ9.NvMY4rM-gyiy-gmLeh_7HYPknSxhv4sJ9OPPM8IzPBJQTLvd--8eKG4GA0HsC5Gu2tBQVYVPAqyc1qUFggpfHQ"

dhan = dhanhq("9884383177",token)

# Replace 'BANKNIFTY 15 NOV 32500 PUT' with the instrument name you want to search
# instrument_name = 'BANKNIFTY 15 NOV 32500 PUT'
instrument_name = 'Nifty Bank'


# Function to retrieve SEM_SMST_SECURITY_ID based on SEM_CUSTOM_SYMBOL
def get_security_id(csv_file, instrument_name):
    print(f"instrument name is {instrument_name}")
    with open(csv_file, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            if row['SEM_CUSTOM_SYMBOL'] == instrument_name:
                return row['SEM_SMST_SECURITY_ID']
    
    return None

# Specify the CSV file path
csv_file_path = 'api-scrip-master.csv'

# Call the function to get the SEM_SMST_SECURITY_ID
security_id = get_security_id(csv_file_path, instrument_name)

if security_id is not None:
    print(f"SEM_SMST_SECURITY_ID for {instrument_name}: {security_id}")
else:
    print(f"Instrument '{instrument_name}' not found in the CSV data.")



# Get the current date
def get_expiry():
    today = datetime.now()

    # Calculate the number of days until the next Wednesday (0 = Monday, 1 = Tuesday, 2 = Wednesday, etc.)
    days_until_wednesday = (2 - today.weekday()) % 7

    # Calculate the date of the next Wednesday
    next_wednesday = today + timedelta(days=days_until_wednesday)

    # Format the date as a string (e.g., 'YYYY-MM-DD')
    next_wednesday_str = next_wednesday.strftime('%d %b').upper()

    # Print the date of the next Wednesday
    print("Next Wednesday's Date:", next_wednesday_str)
    return next_wednesday_str



def get_strike(condition,close):
    strike = round(close/100)*100
    if condition == "BUY":
        right = f"{strike} CALL"
        return right
    if condition == "SELL":
        right = f"{strike} PUT"
        return right    

def place_order(security_id,exchange_seg,type,qty,o_type,p_type,price):
    dhan.place_order(security_id=security_id, 
                        exchange_segment=exchange_seg,
                        transaction_type=type,
                        quantity=qty,
                        order_type=o_type,
                        product_type=p_type,
                        price=price)
    print("Order placed successfully")
def close_positions():
       net_pos = dhan.get_positions()
       if net_pos['data'] is not None:
            for o in net_pos['data']:
                if int(o['netQty']) != 0:
                    direction = "SELL" if int(o['netQty']) > 0 else "BUY"
                    print("Its entered here")
                    print (o["tradingSymbol"])
                    print(direction)
                    print(o['securityId'])
                    print(abs(int(o['netQty'])))
                    # dhan.place_order(security_id=o['securityId'], 
                    #     exchange_segment=dhan.FNO,
                    #     transaction_type=dhan.SELL,
                    #     quantity=o['netQty'],
                    #     order_type=dhan.MARKET,
                    #     product_type=dhan.INTRA,
                    #     price=0)         
                    place_order(o['securityId'],dhan.FNO,dhan.SELL,o['netQty'],dhan.MARKET,dhan.INTRA,price=0)           
                    print("Closed  position successfully")
                    time.sleep(0.2)
            print("No position to close")


def fire(condition,close):
    exp = get_expiry()
    print(exp)
    instrument = "BANKNIFTY"
    stk = get_strike(condition,close)
    print(f"strike is {stk}")
    token = get_security_id('api-scrip-master.csv',f"{instrument} {exp} {stk}")
    print(token)
    close_positions()
    qty = 15
    direction,hlow = option(token)
    if direction != condition:
    #Fix the indentation here 
        place_order(token,dhan.FNO,dhan.BUY,qty,dhan.MARKET,dhan.INTRA,price=0)
        monitor(token,hlow)
    print("Opposing signals")    


def option(token):
    print(token)
    while True:
        data = dhan.intraday_daily_minute_charts(token,"NSE_FNO","OPTIDX")
        intraday_data = pd.DataFrame(data['data'])
        temp_list = []
        for i in intraday_data['start_Time']:
            temp = dhan.convert_to_date_time(i)
            temp_list.append(temp)
        intraday_data['date']  = temp_list
        print(intraday_data)  
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
        # intraday_data_15M.dropna(inplace=True)

        # Reset the index to have 'date' as a column rather than an index
        intraday_data_15M.reset_index(inplace=True)

        # Now you have 'intraday_data_15M' with 15-minute bars OHLC data

        # Con
        # Print the 15M data
        print(intraday_data_15M)

        # Print fund limits

        # Print order lis
        # Calculate candle size (high - low)
        intraday_data_15M['candle_size'] = intraday_data_15M['high'] - intraday_data_15M['low']

        # Calculate candle wick (bear: low, bull: high - close)
        intraday_data_15M['candle_wick'] = intraday_data_15M['high'] - intraday_data_15M['low'] - abs(intraday_data_15M['close'] - intraday_data_15M['open'])

        # Calculate the ratio of candle wick to candle size
        intraday_data_15M['wick_to_size_ratio'] = intraday_data_15M['candle_wick'] / intraday_data_15M['candle_size']

        # Print the updated DataFrame with candle size, candle wick, and ratio
        print(intraday_data_15M[['date', 'candle_size', 'candle_wick', 'wick_to_size_ratio']])

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
                if retracement / body_size_i <= 0.3:
                    # Check if the next candle (i+1) closes higher than its open
                    if intraday_data_15M.at[i + 1, 'close'] > intraday_data_15M.at[i + 1, 'open']:
                        intraday_data_15M.at[i + 1, 'Signal'] = "BUY"
                        last_trade = "BUY"
                    else:
                        intraday_data_15M.at[i + 1, 'Signal'] = "SELL"
                        last_trade = "SELL"
                intraday_data_15M.at[i + 1, 'Signal'] = "NOPE"   
                latest_signal = intraday_data_15M.iloc[-1]['Signal']

                if latest_signal == "BUY" and last_trade != "BUY":
                    print("The latest signal is a BUY signal.")
                elif latest_signal == "SELL" and last_trade != "SELL":
                    print("The latest signal is a SELL signal.")   
                # security.fire(latest_signal,intraday_data_15M.iloc[-1]['close'])    
                if latest_signal  == "BUY":
                    return latest_signal,intraday_data_15M.iloc[-1]['low']
                elif latest_signal == "SELL":
                    return latest_signal,intraday_data_15M.iloc[-1]['high']
                time.sleep(10)            

        # Display the DataFrame with the "Signal" column
        print(intraday_data_15M[['date', 'candle_size', 'candle_wick', 'wick_to_size_ratio', 'Signal']])
    

def monitor(token,hlow):
    while True :
        data = dhan.intraday_daily_minute_charts(token,"NSE_FNO","OPTIDX")
        intraday_data = pd.DataFrame(data['data'])
        temp_list = []
        for i in intraday_data['start_Time']:
            temp = dhan.convert_to_date_time(i)
            temp_list.append(temp)
        intraday_data['date']  = temp_list
        print(intraday_data)  
        intraday_data.set_index('date', inplace=True)
        ltp = intraday_data['close'].iloc[-1]
        sl = max(hlow,0.095*ltp)
        target = 3*sl
        if ltp == target or ltp == sl:
            close_positions()
            break


