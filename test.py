import os
from sqlalchemy import create_engine

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5439")

try:
    engine = create_engine(f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
