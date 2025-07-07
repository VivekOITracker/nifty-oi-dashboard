import streamlit as st
from utils import get_option_chain_data, analyze_oi
import datetime

st.set_page_config(page_title="NIFTY OI Tracker", layout="wide")

if 'last_oi_data' not in st.session_state:
    st.session_state.last_oi_data = None

if 'last_suggestion' not in st.session_state:
    st.session_state.last_suggestion = ""

st.title("📊 NIFTY 50 Open Interest Dashboard")

if st.button("🔄 Refresh Data"):
    # Fetch fresh data only when button is clicked
    df, spot_price = get_option_chain_data()
    suggestion, supports, resistances, target = analyze_oi(df, spot_price)

    # Update session state
    st.session_state.last_oi_data = df
    st.session_state.last_suggestion = suggestion

    # Show last updated timestamp
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🕒 Last updated: {now}")

    # Display live spot price
    st.metric("📌 Spot Price", f"{spot_price:.2f}")
    st.success(f"📊 Suggested Market Move: {suggestion}")

    st.markdown(f"""
    **Support strikes:** {supports}  
    **Resistance strikes:** {resistances}  
    **Target price for trade:** {target if target else 'N/A'}
    """)

    # Show OI table between supports and resistances
    min_strike = min(supports + resistances)
    max_strike = max(supports + resistances)
    df_range = df[(df['Strike'] >= min_strike) & (df['Strike'] <= max_strike)].copy()

    st.subheader("🔍 OI Data between major support and resistance strikes")
    st.dataframe(df_range[['Strike', 'CE_OI', 'PE_OI', 'Total_OI', 'PCR']].reset_index(drop=True), use_container_width=True)

else:
    st.info("⬆ Click the 'Refresh Data' button above to fetch live OI data.")
