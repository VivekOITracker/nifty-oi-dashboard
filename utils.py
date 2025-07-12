import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_option_chain_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/option-chain"
    }

    session = requests.Session()
    session.headers.update(headers)

    # Step 1: Get cookies
    homepage = "https://www.nseindia.com"
    try:
        res = session.get(homepage, timeout=5)
        res.raise_for_status()
    except Exception as e:
        raise ValueError(f"Error accessing NSE homepage: {e}")

    # Step 2: Fetch the option chain
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise ValueError(f"NSE API returned error: {e}")

    spot_price = data['records']['underlyingValue']
    all_data = data['records']['data']

    ce_data, pe_data = [], []

    for item in all_data:
        strike = item.get("strikePrice")
        ce_oi = item.get("CE", {}).get("openInterest", 0)
        pe_oi = item.get("PE", {}).get("openInterest", 0)

        if strike is not None and (ce_oi > 0 or pe_oi > 0):
            ce_data.append([strike, ce_oi])
            pe_data.append([strike, pe_oi])

    df_ce = pd.DataFrame(ce_data, columns=['Strike', 'CE_OI'])
    df_pe = pd.DataFrame(pe_data, columns=['Strike', 'PE_OI'])
    df = df_ce.merge(df_pe, on='Strike', how='outer').fillna(0)
    df['Total_OI'] = df['CE_OI'] + df['PE_OI']
    df['PCR'] = df['PE_OI'] / df['CE_OI'].replace(0, 1)

    # Only keep strikes within ±300 points of spot
    df_filtered = df[(df['Strike'] >= spot_price - 300) & (df['Strike'] <= spot_price + 300)]
    df_filtered = df_filtered.sort_values("Strike").reset_index(drop=True)

    return df_filtered, spot_price


def analyze_oi(df, spot_price):
    # Top 2 supports = Highest PE OI below or at spot
    supports = df[df['Strike'] <= spot_price].sort_values(by='PE_OI', ascending=False).head(2)['Strike'].tolist()

    # Top 2 resistances = Highest CE OI above or at spot
    resistances = df[df['Strike'] >= spot_price].sort_values(by='CE_OI', ascending=False).head(2)['Strike'].tolist()

    supports = sorted(supports)
    resistances = sorted(resistances)

    suggestion = ""
    target = None

    if spot_price < supports[0]:
        suggestion = f"🟢 Bounce expected from strong support at {supports[0]}"
        target = resistances[0] if resistances else None
    elif spot_price > resistances[-1]:
        suggestion = f"🔴 Pullback expected from strong resistance at {resistances[-1]}"
        target = supports[-1] if supports else None
    elif supports and resistances:
        nearest = df.iloc[(df['Strike'] - spot_price).abs().argsort()[:1]]
        strike = nearest['Strike'].values[0]
        ce = nearest['CE_OI'].values[0]
        pe = nearest['PE_OI'].values[0]

        if pe > ce:
            suggestion = "🟢 Bullish bias near spot"
            target = resistances[-1]
        elif ce > pe:
            suggestion = "🔴 Bearish bias near spot"
            target = supports[0]
        else:
            suggestion = "⚪ Range-bound market near spot"
            target = None
    else:
        suggestion = "⚠️ Spot outside monitored range"
        target = None

    return suggestion, supports, resistances, target
