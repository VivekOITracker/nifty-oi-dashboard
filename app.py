import streamlit as st
from utils import get_option_chain_data, analyze_oi
import time

st.set_page_config(page_title="NIFTY OI Tracker", layout="wide")

# Initialize session state to hold last OI snapshot and suggestion
if 'last_oi_data' not in st.session_state:
    st.session_state.last_oi_data = None

if 'last_suggestion' not in st.session_state:
    st.session_state.last_suggestion = ""

REFRESH_INTERVAL_SECONDS = 60  # check every 60 seconds

def is_oi_data_changed(new_df, old_df):
    if old_df is None:
        return True
    # Compare only Strike, CE_OI, PE_OI in the filtered range
    cols_to_check = ['Strike', 'CE_OI', 'PE_OI']
    new_subset = new_df[cols_to_check].reset_index(drop=True)
    old_subset = old_df[cols_to_check].reset_index(drop=True)
    return not new_subset.equals(old_subset)

def main():
    # Get fresh data
    df, spot_price = get_option_chain_data()
    suggestion, supports, resistances, target = analyze_oi(df, spot_price)

    # Show spot price live
    st.metric("📌 Spot Price", f"{spot_price:.2f}")

    # Show suggestion above table and update only if changed
    if suggestion != st.session_state.last_suggestion:
        st.session_state.last_suggestion = suggestion
        st.success(f"📊 Suggested Market Move: {suggestion}")

    # Show support/resistance strikes & target price
    st.markdown(f"""
    **Support strikes:** {supports}  
    **Resistance strikes:** {resistances}  
    **Target price for trade:** {target if target else 'N/A'}
    """)

    # Define monitored range between lowest support and highest resistance
    min_strike = min(supports + resistances)
    max_strike = max(supports + resistances)
    df_range = df[(df['Strike'] >= min_strike) & (df['Strike'] <= max_strike)].copy()

    # Display the OI data table
    st.subheader("🔍 OI Data between major support and resistance strikes")
    st.dataframe(df_range[['Strike', 'CE_OI', 'PE_OI', 'Total_OI', 'PCR']].reset_index(drop=True), use_container_width=True)

    # Check if OI data changed in monitored range
    if is_oi_data_changed(df_range, st.session_state.last_oi_data):
        st.session_state.last_oi_data = df_range.copy()
        # Auto-rerun to fetch fresh data after delay
        time.sleep(REFRESH_INTERVAL_SECONDS)
        st.experimental_rerun()
    else:
        # No change, wait and check again
        time.sleep(REFRESH_INTERVAL_SECONDS)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
