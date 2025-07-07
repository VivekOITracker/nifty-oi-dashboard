import streamlit as st
from utils import get_option_chain_data, analyze_oi
import time

st.set_page_config(page_title="NIFTY OI Tracker", layout="wide")

# Store previous OI data in session state
if 'last_oi_data' not in st.session_state:
    st.session_state.last_oi_data = None

st.title("📊 NIFTY 50 Options OI Dashboard — Smart Auto Refresh")

with st.spinner("Fetching live data..."):
    df, spot_price = get_option_chain_data()
    suggestion, support, resistance = analyze_oi(df, spot_price)

st.metric("📌 Spot Price", f"{spot_price:.2f}")
st.metric("📉 Resistance (Max CE OI)", f"{resistance}")
st.metric("📈 Support (Max PE OI)", f"{support}")

# Filter only strikes between support and resistance
df_range = df[(df['Strike'] >= support) & (df['Strike'] <= resistance)].copy()

st.subheader("🔍 Focused OI Between Support and Resistance")
st.dataframe(df_range.reset_index(drop=True), use_container_width=True)

st.subheader("📈 Suggested Market Move")
st.success(suggestion)

# Compare current vs last OI to decide refresh
refresh_needed = False
if st.session_state.last_oi_data is not None:
    prev_df = st.session_state.last_oi_data
    merged = df_range.merge(prev_df, on="Strike", suffixes=('', '_prev'))
    for _, row in merged.iterrows():
        if row['CE_OI'] != row['CE_OI_prev'] or row['PE_OI'] != row['PE_OI_prev']:
            refresh_needed = True
            break

# Update session state with current OI data
st.session_state.last_oi_data = df_range[['Strike', 'CE_OI', 'PE_OI']].copy()

# If OI changed → auto-refresh every 60 seconds
if refresh_needed:
    st.info("🔄 Change in OI detected — dashboard will refresh in 60 seconds...")
    time.sleep(60)
    st.experimental_rerun()
else:
    st.info("✅ No change in key OI data — no auto-refresh triggered.")
