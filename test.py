import streamlit as st
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL  # ✅ Import this
import pandas as pd

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5439")

# Debug: Print the loaded environment variables
st.write(f"DB_USERNAME: {DB_USERNAME}")
st.write(f"DB_PASSWORD: {DB_PASSWORD}")
st.write(f"DB_HOST: {DB_HOST}")
st.write(f"DB_NAME: {DB_NAME}")
st.write(f"DB_PORT: {DB_PORT}")

try:
    # Create a database engine using SQLAlchemy
    connection_string = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    engine = create_engine(connection_string, connect_args={"options": "-c search_path=public"})

    # Test the connection
    with engine.connect() as conn:
        # Execute a simple query to test the connection
        result = conn.execute("SELECT 1")
        st.write("✅ Database connection very very successful!")
except Exception as e:
    # Print an error message if the connection fails
    st.write(f"❌ Connection failed: {e}")

# Load data
with engine.connect() as connection:
    customers_df = pd.read_sql_query("SELECT * FROM customers", con=connection)
    creditscorehistory_df = pd.read_sql_query("SELECT * FROM creditscorehistory", con=connection)
    loanapplications_df = pd.read_sql_query("SELECT * FROM loanapplications", con=connection)
    mobileusage_df = pd.read_sql_query("SELECT * FROM mobileusage", con=connection)
    transactions_df = pd.read_sql_query("SELECT * FROM transactions", con=connection)
    mobilemoney_df = pd.read_sql_query("SELECT * FROM mobilemoneytransactions", con=connection)

