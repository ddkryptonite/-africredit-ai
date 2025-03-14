import streamlit as st
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5439")

try:
    connection_url = URL.create(
        drivername="redshift+psycopg2",
        username=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    
    engine = create_engine(connection_url)
    
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        st.write("✅ Database connection successful!")
except Exception as e:
    st.write(f"❌ Connection failed: {e}")
