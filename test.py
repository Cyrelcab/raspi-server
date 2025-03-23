import os
import json
import psycopg2
#from dotenv import load_dotenv
from datetime import datetime
import random

# Load environment variables
#load_dotenv()
#DB_URL = os.getenv("DATABASE_URL")
DB_URL = "postgresql://postgres.tsiiblalobzwtzcxuzck:flood-alert-system@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def send_data():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Generate random sensor data
        sensor_data = {
            "flow_rate_1": round(random.uniform(0.0, 10.0), 2),
            "flow_rate_2": round(random.uniform(0.0, 10.0), 2),
            "humidity_1": random.randint(30, 90),
            "humidity_2": random.randint(30, 90),
            "water_level_1": round(random.uniform(0.0, 100.0), 2),
            "water_level_2": round(random.uniform(0.0, 100.0), 2),
            "created_at": datetime.now()
        }

        # Insert data into the database
        columns = ', '.join(sensor_data.keys())
        values = ', '.join(['%s'] * len(sensor_data))
        query = f"INSERT INTO sensor_data ({columns}) VALUES ({values})"
        
        cur.execute(query, list(sensor_data.values()))
        conn.commit()

        print("Random data sent to database:", sensor_data)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Run the function
send_data()
