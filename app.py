import streamlit as st
from utils.utils import get_option_chain_data, analyze_oi
import datetime

st.set_page_config(page_title="NIFTY OI Tracker", layout="wide")

# Session state to persist data across refreshes
if 'last_oi_data' not in st.session_state:
    st.session_state.last_oi_data = None
if 'last_suggestion' not in st.session_state:
    st.session_state.last_suggestion = ""
if 'last_spot_price' not in st.session_state:
    st.session_state.last_spot_price = None
if 'last_supports' not in st.session_state:
    st.session_state.last_supports = []
if 'last_resistances' not in st.session_state:
    st.session_state.last_resistances = []
if 'last_target' not in st.session_state:
    st.session_state.last_target = None
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None

st.title("📊 NIFTY 50 Open Interest Dashboard")

# Manual refresh button
if st.button("🔄 Refresh Data"):
    try:
        df, spot_price = get_option_chain_data()
        suggestion, supports, resistances, target = analyze_oi(df, spot_price)

        # Store results in session state
        st.session_state.last_oi_data = df
        st.session_state.last_suggestion = suggestion
        st.session_state.last_spot_price = spot_price
        st.session_state.last_supports = supports
        st.session_state.last_resistances = resistances
        st.session_state.last_target = target
        st.session_state.last_updated = datetime.datetime.now()

        # Display live results
        st.metric("📌 Spot Price", f"{spot_price:.2f}")
        st.success(f"📊 Suggested Market Move: {suggestion}")
        st.caption(f"🕒 Last updated: {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

        st.markdown(f"""
        **Support Strikes:** {supports}  
        **Resistance Strikes:** {resistances}  
        **Target Price (approx):** {target if target else 'N/A'}
        """)

        # Display filtered OI data between major support/resistance
        min_strike = min(supports + resistances)
        max_strike = max(supports + resistances)
        df_range = df[(df['Strike'] >= min_strike) & (df['Strike'] <= max_strike)]

        st.subheader("🔍 OI Data between Major Support and Resistance")
        st.dataframe(
            df_range[['Strike', 'CE_OI', 'PE_OI', 'Total_OI', 'PCR']].reset_index(drop=True),
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Error fetching or processing data: {e}")

# If no refresh, show last data if available
else:
    st.info("⬆ Click the **Refresh Data** button above to load the latest OI data.")
    if st.session_state.last_oi_data is not None:
        st.metric("📌 Spot Price", f"{st.session_state.last_spot_price:.2f}")
        st.success(f"📊 Suggested Market Move: {st.session_state.last_suggestion}")
        st.caption(f"🕒 Last updated: {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

        st.markdown(f"""
        **Support Strikes:** {st.session_state.last_supports}  
        **Resistance Strikes:** {st.session_state.last_resistances}  
        **Target Price (approx):** {st.session_state.last_target if st.session_state.last_target else 'N/A'}
        """)

        df = st.session_state.last_oi_data
        min_strike = min(st.session_state.last_supports + st.session_state.last_resistances)
        max_strike = max(st.session_state.last_supports + st.session_state.last_resistances)
        df_range = df[(df['Strike'] >= min_strike) & (df['Strike'] <= max_strike)]

        st.subheader("🔍 OI Data between Major Support and Resistance")
        st.dataframe(
            df_range[['Strike', 'CE_OI', 'PE_OI', 'Total_OI', 'PCR']].reset_index(drop=True),
            use_container_width=True
        )
