import streamlit as st
from utils import get_option_chain_data, analyze_oi
import time

st.set_page_config(page_title="NIFTY OI Tracker", layout="wide")

if 'last_oi_data' not in st.session_state:
    st.session_state.last_oi_data = None

if 'last_suggestion' not in st.session_state:
    st.session_state.last_suggestion = ""

df, spot_price = get_option_chain_data()
suggestion, supports, resistances, target = analyze_oi(df, spot_price)

# Show spot price live
st.metric("📌 Spot Price", f"{spot_price:.2f}")

# Show suggestion above table and update only on change
if suggestion != st.session_state.last_suggestion:
    st.session_state.last_suggestion = suggestion
    st.success(f"📊 Suggested Market Move: {suggestion}")

# Show support/resistance strikes & target
st.markdown(f"""
**Support strikes:** {supports}  
**Resistance strikes:** {resistances}  
**Target price for trade:** {target if target else 'N/A'}
""")

# Filter data between lowest support and highest resistance
min_strike = min(supports + resistances)
max_strike = max(supports + resistances)
df_range = df[(df['Strike'] >= min_strike) & (df['Strike'] <= max_strike)].copy()

# Display the full strike prices with OI correctly
st.subheader("🔍 OI Data between major support and resistance strikes")
st.dataframe(df_range[['Strike', 'CE_OI', 'PE_OI', 'Total_OI', 'PCR']].reset_index(drop=True), use_container_width=True)

# Auto-refresh logic here (as before) based on OI changes in df_range...

# ... rest of your code to handle refresh as before ...
