from datetime import datetime, timedelta
import pandas as pd
import time
quantity = 15
import json
from kiteconnect import KiteConnect
key = "9gdjvyog0alqsyll"
# Open the JSON file and load the data
with open('access_token.json', 'r') as file:
    data = json.load(file)

# Access the 'access_token' from the loaded data
access_token = data.get('access_token')
kite = KiteConnect(api_key=key)
kite.set_access_token(access_token)

# Print or use the access_token as needed
print(f"Access Token: {access_token}")
def fire(condition):
    if condition == 1:
        direction ="BUY"
        option_type = "CE"
    elif condition == -1 :
        direction = "SELL" 
        option_type = "PE"   
    exp = get_exp().upper()
    stk = get_stk(direction)
    contract_name = "BANKNIFTY"
    order_info = f"{contract_name}{exp}{stk}{option_type}"
    place_order(order_info,quantity)
    monitor(order_info,direction)


def get_exp():
    current_date = datetime.now()
    day_of_week = current_date.weekday()
    days_until_wednesday = (2 - day_of_week + 7) % 7
    nearest_wednesday_date = current_date + timedelta(days=days_until_wednesday)

    if nearest_wednesday_date.month != (nearest_wednesday_date + timedelta(days=7)).month:
        # Last week of the month, return in the format "YYMON"
        return nearest_wednesday_date.strftime('%y%b')
    else:
        # Regular case, return in the format "YYMMDD"
        return nearest_wednesday_date.strftime('%y%m%d')
    
def get_stk(condition) :
    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    print(banknifty_ltp)
    strike_price = round(banknifty_ltp / 1000) * 1000
    
    if condition == "BUY":
        return strike_price + 1800
    elif condition == "SELL":
        return strike_price - 1800
    else:
        return strike_price

def place_order(instrument,qty):
    print(instrument)
    kite.place_order(variety = kite.VARIETY_REGULAR,exchange="NFO",
        tradingsymbol=instrument,
        transaction_type="BUY",
        quantity=qty,
        order_type="MARKET",
        product="MIS",
        validity="DAY",
        price=0,
        trigger_price=0)
    print("Position entered successfully")

def square_off_all_positions():
    # Fetch current positions
    positions = kite.positions()
    
    # Iterate through each position type ('net', 'day')
    for position_type in ['net']:
        # Iterate through positions of the current type
        for position in positions.get(position_type, []):
            # Extract relevant information
            tradingsymbol = position['tradingsymbol']
            quantity = position['quantity']
            if quantity > 0 :

            # Place a market sell order to square off the position
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=tradingsymbol,
                                            transaction_type=kite.TRANSACTION_TYPE_SELL,
                                            quantity=quantity,
                                            product=kite.PRODUCT_MIS,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            tag="SquareOff")

                # Print information about the square off order
                print(f"Square off order placed for {tradingsymbol} with order id {order_id}")
            else :
                print("No order to square off ")    

def calculate_and_log_pnl():
    orders = kite.orders()
    for order in orders:
        if order['status'] == 'COMPLETE':
            entry_price, exit_price = get_entry_and_exit_prices(order['order_id'])
            quantity = order['quantity']
            pnl = (exit_price - entry_price) * quantity
            return pnl

def get_entry_and_exit_prices(order_id):
    order_info = kite.order_history(order_id)
    entry_price = order_info['average_price']
    exit_price = order_info['trigger_price']
    return entry_price, exit_price           

 

def get_renko(timestamps, close, step):
    prices = close
    first_brick = {
        'timestamp': timestamps[0],
        'open': round(prices.iloc[0] / step) * step,
        'close': round((prices.iloc[0] / step)+1) * step
    }
    bricks = [first_brick]
    for price, timestamp in zip(prices, timestamps):
        if price > (bricks[-1]['close'] + step):
            step_mult = round((price - bricks[-1]['close']) / step)
            next_bricks = [{
                'timestamp': timestamp,
                'open': bricks[-1]['close'] + (mult * step),
                'close': bricks[-1]['close'] + ((mult + 1) * step)
            } for mult in range(1, step_mult)]
            bricks += next_bricks

        elif price < (bricks[-1]['open'] - step):
            step_mult = round((bricks[-1]['open'] - price) / step)
            next_bricks = [{
                'timestamp': timestamp,
                'open': bricks[-1]['close'] - ((mult + 1) * step),
                'close': bricks[-1]['close'] - (mult * step)
            } for mult in range(1, step_mult + 1)]
            bricks += next_bricks

    df = pd.DataFrame(bricks)
    df['high'] = df['close'].shift(-1)
    df['low'] = df['open'].shift(-1)
    df = df[:-1]

    return df

def cancel_orders():
    orders = kite.orders()
    print(orders)
    for order in orders:
        if order["status"] == "OPEN" or order["pending_quantity"] > 0:
            order_id = order["order_id"]
            print(order_id)
            kite.cancel_order(kite.VARIETY_REGULAR,order_id)
            print(f"Order {order_id} cancelled")

def monitor(instrument,direction):
    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    mark_price = banknifty_ltp
    sl_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   exchange=kite.EXCHANGE_NFO,
                                   tradingsymbol=instrument,
                                   transaction_type=kite.TRANSACTION_TYPE_SELL,
                                   quantity=quantity,
                                   product=kite.PRODUCT_NRML,
                                   order_type=kite.ORDER_TYPE_SL,
                                   price=mark_price - 40,
                                   tag="SL")
    print(f"Stop loss order placed for BankNifty with order id {sl_order_id}")
    to_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    from_date = (pd.Timestamp.now() - pd.DateOffset(days=5)).strftime('%Y-%m-%d')
    instrument_token = 260105
    # Fetch historical data for Bank Nifty within the specified date range
    raw_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval="minute")
    nifty_data = pd.DataFrame(raw_data)
    nifty_data['timestamp'] = pd.to_datetime(nifty_data['date'], unit='ms')
    
    while True:
        # Fetch new data and convert it to a DataFrame
        new_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval="minute")
        new_data_df = pd.DataFrame(new_data)

        # Check if 'timestamp' is present in the columns
        if 'date' in new_data_df.columns:
            # Convert the 'timestamp' column to datetime
            new_data_df['timestamp'] = pd.to_datetime(new_data_df['date'], unit='ms')

            # Append the new data to the existing dataframe
            nifty_data = nifty_data._append(new_data_df, ignore_index=True)

            # Call the get_renko function and print the resulting DataFrame
            renko_bricks = get_renko(new_data_df['timestamp'],nifty_data['close'], 20)
            renko_df = pd.DataFrame(renko_bricks, columns=['timestamp', 'open', 'close', 'high', 'low'])
            if direction == "BUY" and renko_df['close'].iloc[-1] < renko_df['open'].iloc[-1]:
                square_off_all_positions()
                cancel_orders()
                break
            elif direction == "SELL" and renko_df['close'].iloc[-1] > renko_df['open'].iloc[-1]:
                square_off_all_positions()
                cancel_orders()
                break
            time.sleep(60)

# print(get_exp().upper())  
# cancel_orders()         
square_off_all_positions()
print(calculate_and_log_pnl())
print(get_entry_and_exit_prices)