import csv
from datetime import datetime, timedelta
from dhanhq import dhanhq
import time
import pandas as pd
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzAzMzAyNzMxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDY0MDMxNyJ9.NvMY4rM-gyiy-gmLeh_7HYPknSxhv4sJ9OPPM8IzPBJQTLvd--8eKG4GA0HsC5Gu2tBQVYVPAqyc1qUFggpfHQ"
phone = "9884383177"
dhan = dhanhq(phone,token)

# Replace 'BANKNIFTY 15 NOV 32500 PUT' with the instrument name you want to search
# instrument_name = 'BANKNIFTY 15 NOV 32500 PUT'
instrument_name = 'Nifty Bank'


# Function to retrieve SEM_SMST_SECURITY_ID based on SEM_CUSTOM_SYMBOL
def get_security_id(csv_file, instrument_name):
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
    instrument = "BANKNIFTY"
    stk = get_strike(condition,close)
    print(stk)
    name  = f"{instrument} {exp} {stk}"
    token = get_security_id('api-scrip-master.csv',name)
    print(token)
    close_positions()
    qty = 15
    options_close = option_close(token)
    sl = option(token,options_close)
    if(sl):
        place_order(token,dhan.FNO,dhan.BUY,qty,dhan.MARKET,dhan.INTRA,price=0)
        print("Yay trade entered")
        monitor(token,sl,name,qty)
    print("Opposing signals")   

def option_close(token) :
    print(type(token))
    print(f"token is {token}")
    data = dhan.intraday_daily_minute_charts(
    security_id=token,
    exchange_segment='NSE_FNO',
    instrument_type='OPTIDX'
    )
    if data['data']:
        intraday_data = pd.DataFrame(data['data'])
        temp_list = [dhan.convert_to_date_time(i) for i in intraday_data['start_Time']]
        intraday_data['date'] = temp_list
        intraday_data.set_index('date', inplace=True)
        ltp = intraday_data['close'].iloc[-1]
        return ltp
    else:
        print("No data")



def option(token, close_pv):
    print(f"{close_pv} is previous close")
    min_low = float('inf')  # Initialize min_low to positive infinity

    while True:
        # Fetch data for 1-minute candle
        data = dhan.intraday_daily_minute_charts(
            security_id=token,
            exchange_segment='NSE_FNO',
            instrument_type='OPTIDX'
        )
        time.sleep(1)
        intraday_data = pd.DataFrame(data['data'])
        temp_list = [dhan.convert_to_date_time(i) for i in intraday_data['start_Time']]
        intraday_data['date'] = temp_list
        intraday_data.set_index('date', inplace=True)
        ltp = intraday_data['close'].iloc[-1]
        print(ltp)
        time.sleep(60)
        
        if ltp > close_pv:
            sl = max(min_low, 0.95 * ltp)
            return sl

        min_low = min(min_low, intraday_data['low'].iloc[-1])
        print(f"{min_low} is min_low")
    





def monitor(token, hlow,name,qty):
    ltp = option_close(token)
    sl = hlow
    sl_calc = abs(ltp - sl)
    target_sl = sl_calc * 1
    target_calc = ltp 
    print(f"{sl} and {target_calc}")
    csv_file_path = 'trades.csv'

    # Create a CSV file and write header if it doesn't exist
    fieldnames = ['Timestamp', 'Instrument', 'Entry', 'Exit', 'Lots', 'PNL']
    try:
        with open(csv_file_path, 'x', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
    except FileExistsError:
        # File already exists
        pass

    while ltp <= target_calc and ltp >= sl:
        data = dhan.intraday_daily_minute_charts(token, "NSE_FNO", "OPTIDX")
        intraday_data = pd.DataFrame(data['data'])
        temp_list = [dhan.convert_to_date_time(i) for i in intraday_data['start_Time']]
        intraday_data['date'] = temp_list
        intraday_data.set_index('date', inplace=True)
        ltp = intraday_data['close'].iloc[-1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"{ltp} is option ltp")

        # Append data to CSV file
        time.sleep(1)

    close_ltp = option_close(token)
    pnl = (close_ltp - ltp) * qty
    close_positions()

    with open(csv_file_path, 'a', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writerow({
            'Timestamp': timestamp,
            'Instrument': name,
            'Entry': ltp,
            'Exit': close_ltp,
            'Lots': qty,
            'PNL': pnl
        })

# fire("SELL",44649)
# close_positions()
