import pandas as pd
import datetime
import time
import math
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from pyotp import TOTP
import time
from kiteconnect import KiteConnect
import pandas_ta as ta
import mplfinance as fplt
import json
import os
import security

# Assuming kite connect object is created and named as kite
# e.g., kite = KiteConnect(api_key="YOUR_API_KEY")
# kite.set_access_token("YOUR_ACCESS_TOKEN")

def autologin():
    try:
        token_path = "api_key.txt"
        key, secret, username, password, totp_secret = open(token_path, 'r').read().split()

        # Create a Chrome WebDriver instance
        driver = webdriver.Chrome()
        logging.info("WebDriver instance created")

        # Initialize KiteConnect with your API key
        kite = KiteConnect(api_key=key)
        logging.info("KiteConnect initialized")

        # Check if access token is stored for today
        stored_token = get_stored_token()
        if stored_token and is_same_day(stored_token['timestamp']):
            kite.set_access_token(stored_token['access_token'])
            logging.info("Using stored access token.")
            return kite

        # Initialize KiteConnect with your API key
        kite = KiteConnect(api_key=key)
        logging.info("KiteConnect initialized")

        # Open the Kite login page
        driver.get(kite.login_url())
        driver.implicitly_wait(10)
        logging.info("Kite login page opened")

        # Fill in the username and password fields
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))

        logging.info("Username and password fields located")

        username_input.send_keys(username)
        password_input.send_keys(password)

        # Click the "Login" button
        login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div/div/div/form/div[4]/button')))
        login_button.click()
        logging.info("Clicked the 'Login' button")
        time.sleep(2)

        # Generate TOTP
        totp = TOTP(totp_secret)
        token = totp.now()

        # Locate the TOTP input field and submit button
        totp_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[2]/button')))

        totp_input.send_keys(token)
        submit_button.click()
        logging.info("Filled TOTP and clicked 'Submit'")
        time.sleep(5)

        # Wait for successful login  # Replace with the URL you expect after login
        logging.info("Successfully logged in")

        # Extract the request token from the URL
        url = driver.current_url
        initial_token = url.split('request_token=')[1]
        request_token = initial_token.split('&')[0]
        print(request_token)

        # Close the WebDriver
        driver.quit()
        logging.info("WebDriver closed")

        # Initialize KiteConnect again with your API key and the new access token
        kite = KiteConnect(api_key=key)
        data = kite.generate_session(request_token,secret)
        kite.set_access_token(data["access_token"])
        print(data)
        logging.info("Jarvis Enabled")
        store_access_token(kite.access_token)
        return kite

       
    except StaleElementReferenceException:
        logging.error("Stale element reference: The element is no longer valid.")
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")

def get_stored_token():
    token_path = "access_token.json"

    if os.path.isfile(token_path):
        with open(token_path, 'r') as file:
            return json.load(file)

    return None

def store_access_token(access_token):
    token_path = "access_token.json"
    data = {
        'access_token': access_token,
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d')
    }

    with open(token_path, 'w') as file:
        json.dump(data, file)
        logging.info("Access token stored.")

def is_same_day(stored_timestamp):
    return pd.Timestamp.now().strftime('%Y-%m-%d') == stored_timestamp
def fetch_nifty_data():
    instrument_token = 260105  # Replace with the actual instrument token for Bank Nifty
    last_trade = None
    # Calculate from_date and to_date
    to_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    from_date = (pd.Timestamp.now() - pd.DateOffset(days=5)).strftime('%Y-%m-%d')

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

            # Add Awesome Oscillator (AO) to Renko DataFrame
            renko_df['ao'] = ta.ao(renko_df['high'], renko_df['low'])

            # Reset the index to make 'date' a regular column
            renko_df.reset_index(inplace=True)

            # Calculate Donchian Channels for Renko DataFrame
            donchian_df = ta.donchian(renko_df['high'], renko_df['low'], 10, 10)

            # Merge the calculated Donchian Channels with the Renko DataFrame
            renko_df = pd.concat([renko_df, donchian_df], axis=1)

            # Set 'timestamp' column in Renko DataFrame to match the original 'timestamp'
            renko_df['timestamp'] = nifty_data['timestamp']
            latest_close = renko_df['close'].iloc[-1]
            latest_ao = renko_df['ao'].iloc[-1]
            latest_du = renko_df['DCU_10_10'].iloc[-1]
            latest_dl = renko_df['DCL_10_10'].iloc[-1]
            print("Renko Data:")
            print(renko_df)
            if latest_close > latest_du and latest_ao > 0 and last_trade != "BUY":
                security.fire(1,kite)
                last_trade = "BUY"
            elif latest_close < latest_dl and latest_ao <0 and last_trade != "SELL":
                security.fire(-1,kite)
                last_trade = "SELL"
        else:
            print("Timestamp column not found in new data.")

        time.sleep(60)
 

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

# def get_renko(timestamps, close, step):
#     prices = close
#     first_brick = math.floor(prices.iloc[0] / step) * step
#     bricks = [{'timestamp': timestamps.iloc[0], 'close': first_brick}]
    
#     for price, timestamp in zip(prices, timestamps):
#         if price > (bricks[-1]['close'] + step):
#             step_mult = math.floor((price - bricks[-1]['close']) / step)
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'],
#                 'close': bricks[-1]['close'] + ((mult + 1) * step),
#             } for mult in range(1, step_mult + 1)]
#             bricks += next_bricks
#         elif price < (bricks[-1]['close'] - step):
#             step_mult = math.ceil((bricks[-1]['close'] - price) / step)
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'] - (mult * step),
#                 'close': bricks[-1]['close'],
#             } for mult in range(1, step_mult)]
#             bricks += next_bricks
#         else:
#             continue
    
#     df = pd.DataFrame(bricks)
#     df['high'] = df['close'].shift(-1)
#     df['low'] = df['open'].shift(-1)
#     df = df[:-1]

#     return df

# def get_renko(prices, step):
#     first_brick_close = math.floor(prices.iloc[0] / step) * step
#     bricks = [{'timestamp': prices.index[0],
#                'open': first_brick_close,
#                'close': first_brick_close,
#                'high': first_brick_close + step,
#                'low': first_brick_close}]

#     for price, timestamp in zip(prices, prices.index):
#         if price > (bricks[-1]['close'] + step):
#             step_mult = math.floor((price - bricks[-1]['close']) / step)
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'],
#                 'close': bricks[-1]['close'] + ((mult + 1) * step),
#                 'high': bricks[-1]['close'] + ((mult + 1) * step),
#                 'low': bricks[-1]['close'] + (mult * step),
#             } for mult in range(1, step_mult + 1)]
#             bricks += next_bricks
#         elif price < (bricks[-1]['close'] - step):
#             step_mult = math.ceil((bricks[-1]['close'] - price) / step)
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'] - (mult * step),
#                 'close': bricks[-1]['close'],
#                 'high': bricks[-1]['close'],
#                 'low': bricks[-1]['close'] - (mult * step),
#             } for mult in range(1, step_mult)]
#             bricks += next_bricks
#         else:
#             continue

#     return bricks






kite = autologin()
banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
print(banknifty_ltp)
print(kite)
# nfo = kite.instruments("NFO")
# nfo_data = pd.DataFrame(nfo)
# nfo_data.to_csv('nfo_data.csv', index=False)
# Run the function to fetch data
# fetch_nifty_data()
security.fire(1)