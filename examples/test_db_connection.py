"""
Test PostgreSQL connection.
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host="localhost",
        database="travel_companion",
        user="postgres",
        password="postgres"  # PROMENI ako imaš drugačiji password
    )
    print("✅ PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")