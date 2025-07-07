import requests
import pandas as pd

def get_option_chain_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url, timeout=5)
    data = response.json()

    spot_price = data['records']['underlyingValue']
    all_data = data['records']['data']

    ce_data, pe_data = [], []

    for item in all_data:
        strike = item.get("strikePrice")
        if 'CE' in item and 'PE' in item:
            ce_oi = item['CE'].get("openInterest", 0)
            pe_oi = item['PE'].get("openInterest", 0)
            ce_data.append([strike, ce_oi])
            pe_data.append([strike, pe_oi])

    df_ce = pd.DataFrame(c_
