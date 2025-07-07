import streamlit as st
from utils import get_option_chain_data, analyze_oi

st.set_page_config(page_title="NIFTY OI Dashboard", layout="wide")

st.title("📊 Live NIFTY 50 Options Open Interest Dashboard")

data = get_option_chain_data()
signal = analyze_oi(data)

st.dataframe(data)

st.subheader("📈 Suggested Market Move")
st.success(signal)
