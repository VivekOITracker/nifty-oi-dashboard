import requests
import pandas as pd
import time

def get_option_chain_data(retries=3, delay=2):
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
        "Origin": "https://www.nseindia.com"
    }

    session = requests.Session()
    session.headers.update(headers)

    # Attempt retries
    for attempt in range(retries):
        try:
            # Initial request to homepage to get cookies
            response_home = session.get("https://www.nseindia.com", timeout=5)
            if response_home.status_code != 200:
                raise Exception(f"Homepage request failed with status {response_home.status_code}")

            # Now request option chain API with cookies set
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                break  # success, exit retry loop
            else:
                raise Exception(f"NSE API returned status {response.status_code}")

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue  # retry
            else:
                # Raise the last exception after max retries
                raise e

    spot_price = data['records']['underlyingValue']
    all_data = data['records']['data']

    ce_data, pe_data = [], []

    for item in all_data:
        strike = item.get("strikePrice")
        ce_oi = item.get("CE", {}).get("openInterest", 0)
        pe_oi = item.get("PE", {}).get("openInterest", 0)

        if strike is not None and (ce_oi != 0 or pe_oi != 0):
            ce_data.append([strike, ce_oi])
            pe_data.append([strike, pe_oi])

    df_ce = pd.DataFrame(ce_data, columns=['Strike', 'CE_OI'])
    df_pe = pd.DataFrame(pe_data, columns=['Strike', 'PE_OI'])
    df = df_ce.merge(df_pe, on='Strike')
    df['Total_OI'] = df['CE_OI'] + df['PE_OI']
    df['PCR'] = df['PE_OI'] / df['CE_OI'].replace(0, 1)

    df_filtered = df[(df['Strike'] >= spot_price - 300) & (df['Strike'] <= spot_price + 300)]
    df_filtered = df_filtered.sort_values("Strike").reset_index(drop=True)

    return df_filtered, spot_price
