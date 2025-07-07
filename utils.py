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

    df_ce = pd.DataFrame(ce_data, columns=['Strike', 'CE_OI'])
    df_pe = pd.DataFrame(pe_data, columns=['Strike', 'PE_OI'])
    df = df_ce.merge(df_pe, on='Strike')
    df['Total_OI'] = df['CE_OI'] + df['PE_OI']
    df['PCR'] = df['PE_OI'] / df['CE_OI'].replace(0, 1)

    # Filter ±300 points around spot (adjustable)
    df_filtered = df[(df['Strike'] >= spot_price - 300) & (df['Strike'] <= spot_price + 300)]
    df_filtered = df_filtered.sort_values("Strike")

    return df_filtered, spot_price


def analyze_oi(df, spot_price):
    # Determine support and resistance
    support_strike = df.loc[df['PE_OI'].idxmax(), 'Strike']
    resistance_strike = df.loc[df['CE_OI'].idxmax(), 'Strike']

    suggestion = ""

    if spot_price < support_strike:
        suggestion = f"🟢 Possible bounce from support at {support_strike}"
    elif spot_price > resistance_strike:
        suggestion = f"🔴 Possible pullback from resistance at {resistance_strike}"
    elif support_strike < spot_price < resistance_strike:
        # Round spot price to nearest strike in df
        nearest_strike = df.iloc[(df['Strike'] - spot_price).abs().argsort()[:1]]['Strike'].values[0]
        pe_near = df[df['Strike'] == nearest_strike]['PE_OI'].values[0]
        ce_near = df[df['Strike'] == nearest_strike]['CE_OI'].values[0]

        if pe_near > ce_near:
            suggestion = "🟢 Market shows bullish bias near spot"
        elif ce_near > pe_near:
            suggestion = "🔴 Market shows bearish bias near spot"
        else:
            suggestion = "⚪ Market is range-bound near spot"
    else:
        suggestion = "⚠️ Spot is outside monitored zone"

    return suggestion, support_strike, resistance_strike
