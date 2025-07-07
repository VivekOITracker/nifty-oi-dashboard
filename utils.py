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
    ce_data, pe_data = [], []

    for item in data['records']['data']:
        if 'CE' in item and 'PE' in item:
            ce = item['CE']
            pe = item['PE']
            ce_data.append([ce['strikePrice'], ce['openInterest']])
            pe_data.append([pe['strikePrice'], pe['openInterest']])

    df_ce = pd.DataFrame(ce_data, columns=['Strike', 'CE_OI'])
    df_pe = pd.DataFrame(pe_data, columns=['Strike', 'PE_OI'])
    df = df_ce.merge(df_pe, on='Strike')
    df['PCR'] = df['PE_OI'] / df['CE_OI']
    return df

def analyze_oi(df):
    max_ce_strike = df.loc[df['CE_OI'].idxmax(), 'Strike']
    max_pe_strike = df.loc[df['PE_OI'].idxmax(), 'Strike']

    if max_pe_strike > max_ce_strike:
        return f"Market Bias: Bullish (Support at {max_pe_strike}, Resistance at {max_ce_strike})"
    elif max_ce_strike > max_pe_strike:
        return f"Market Bias: Bearish (Resistance at {max_ce_strike}, Support at {max_pe_strike})"
    else:
        return "Range Bound Market"
