import streamlit as st
import os
from sqlalchemy import create_engine

# Get environment variables safely
DB_USERNAME = os.getenv("DB_USERNAME", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Danieledem_7")
DB_HOST = os.getenv("DB_HOST", "streamlit-workgroup.481665119502.eu-north-1.redshift-serverless.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "dev")
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
    
    engine = create_engine(connection_url, connect_args={"options": "-c standard_conforming_strings=off"})

    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        st.write("✅ Database connection successful!")
except Exception as e:
    st.write(f"❌ Connection failed: {e}")

