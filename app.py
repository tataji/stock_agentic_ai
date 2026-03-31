import streamlit as st
from kiteconnect import KiteConnect
from agent import create_trading_crew
import pandas as pd

import streamlit as st
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Access them using os.getenv
API_KEY = os.getenv("KITE_API_KEY")
API_SECRET = os.getenv("KITE_API_SECRET")

# Validation check
if not API_KEY or not API_SECRET:
    st.error("Missing API Keys! Please check your .env file.")
    st.stop()


# --- Configuration ---
#API_KEY = st.secrets["KITE_API_KEY"]
#API_SECRET = st.secrets["KITE_API_SECRET"]
# Redirect URL must match what you set in the Zerodha Developer Console
REDIRECT_URL = "http://localhost:8501" 

st.set_page_config(page_title="Agentic Trader", layout="wide")
st.title("🤖 Agentic AI Trading Terminal (NSE)")

# --- OAuth Login Flow ---
kite = KiteConnect(api_key=API_KEY)

if "access_token" not in st.session_state:
    # Check if we are returning from Zerodha with a request_token
    query_params = st.query_params
    if "request_token" in query_params:
        try:
            request_token = query_params["request_token"]
            data = kite.generate_session(request_token, api_secret=API_SECRET)
            st.session_state["access_token"] = data["access_token"]
            st.success("Login Successful!")
            st.rerun()
        except Exception as e:
            st.error(f"Login Failed: {e}")
    else:
        # Display Login Button if no session exists
        login_url = kite.login_url()
        st.info("Please login to Zerodha to start trading.")
        st.link_button("Login to Zerodha", login_url)
        st.stop()

# Set the token for all subsequent calls
kite.set_access_token(st.session_state["access_token"])

# --- Main Dashboard ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Settings")
    symbol = st.selectbox("Select Stock", ["RELIANCE", "TCS", "INFY", "HDFCBANK"])
    qty = st.number_input("Quantity", min_value=1, value=5)
    
    if st.button("Run AI Analysis"):
        # Fetching basic market data
        quote = kite.quote(f"NSE:{symbol}")[f"NSE:{symbol}"]
        stock_context = f"Price: {quote['last_price']}, High: {quote['ohlc']['high']}, Low: {quote['ohlc']['low']}"
        
        with st.spinner("Agents are debating..."):
            crew = create_trading_crew(stock_context)
            result = crew.kickoff()
            st.session_state["last_signal"] = result
            st.write(result)

with col2:
    st.header("Portfolio & Execution")
    if "last_signal" in st.session_state:
        if st.button(f"Execute {symbol} Trade", type="primary"):
            try:
                # Example: Placing an Intraday (MIS) Market Order
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=kite.EXCHANGE_NSE,
                    tradingsymbol=symbol,
                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                    quantity=qty,
                    product=kite.PRODUCT_MIS,
                    order_type=kite.ORDER_TYPE_MARKET
                )
                st.success(f"Order Placed! ID: {order_id}")
            except Exception as e:
                st.error(f"Execution Error: {e}")

    # Display Live Holdings
    holdings = pd.DataFrame(kite.holdings())
    if not holdings.empty:
        st.subheader("Your Holdings")
        st.dataframe(holdings[['tradingsymbol', 'quantity', 'last_price', 'pnl']])
