import streamlit as st
import os
import pandas as pd
from sqlalchemy import create_engine

# Load environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5439")

# Initialize database connection
try:
    connection_url = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    
    engine = create_engine(connection_url, connect_args={"options": "-c search_path=public"})


    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        st.write("✅ Database connection successful!")

except Exception as e:
    st.write(f"❌ Connection failed: {e}")
    engine = None  # Prevent further errors if the connection fails

# Load data only if connection is successful
if engine:
    try:
        with engine.connect() as conn:
            customers_df = pd.read_sql_query("SELECT * FROM customers", con=conn.connection)
            creditscorehistory_df = pd.read_sql_query("SELECT * FROM creditscorehistory", con=conn.connection)
            loanapplications_df = pd.read_sql_query("SELECT * FROM loanapplications", con=conn.connection)
            mobileusage_df = pd.read_sql_query("SELECT * FROM mobileusage", con=conn.connection)
            transactions_df = pd.read_sql_query("SELECT * FROM transactions", con=conn.connection)
            mobilemoney_df = pd.read_sql_query("SELECT * FROM mobilemoneytransactions", con=conn.connection)
        
        st.write("✅ Data loaded successfully!")

    except Exception as e:
        st.write(f"❌ Data loading failed: {e}")


st.write("Columns in mobilemoney_df:", mobilemoney_df.columns)

mobilemoney_features = mobilemoney_df.groupby('customerid').agg({'amount': ['sum', 'mean', 'count'], 'Balance': 'mean'}).reset_index()
mobilemoney_features.columns = ['customerid', 'totalmobilemoneyamount', 'averagemobilemoneyamount', 'mobilemoneytransactioncount', 'averagemobilemoneybalance']


