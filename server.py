import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import serial

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def send_data():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Configure serial connection for GSM module
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust port and baud rate as needed

        # Initialize empty dictionary for sensor data
        sensor_data = {
            "flow_rate_1": 0.0,
            "flow_rate_2": 0.0,
            "humidity_1": 0,
            "humidity_2": 0,
            "water_level_1": 0.0,
            "water_level_2": 0.0
        }

        # Read data from GSM module
        while True:
            if ser.in_waiting > 0:
                message = ser.readline().decode('utf-8').strip()
                try:
                    # Assuming message format: "PHONE_NUMBER:flow_rate,humidity,water_level"
                    phone, data = message.split(':')
                    flow_rate, humidity, water_level = map(float, data.split(','))
                
                    # Update sensor data based on phone number
                    if phone == "PHONE1":  # Replace with actual phone number
                        sensor_data["flow_rate_1"] = flow_rate
                        sensor_data["humidity_1"] = int(humidity)
                        sensor_data["water_level_1"] = water_level
                    elif phone == "PHONE2":  # Replace with actual phone number
                        sensor_data["flow_rate_2"] = flow_rate
                        sensor_data["humidity_2"] = int(humidity)
                        sensor_data["water_level_2"] = water_level
                    
                    # Update timestamp when data is actually received
                    sensor_data["created_at"] = datetime.now()

                    # Delete all SMS messages
                    ser.write(b'AT+CMGD=1,4\r\n')  # Delete all messages
                    ser.readline()  # Read response
                    break  # Exit loop after receiving data from both sensors
                except Exception as e:
                    print(f"Error parsing message: {e}")
                    continue

        # Insert data into your table
        columns = ', '.join(sensor_data.keys())
        values = ', '.join(['%s'] * len(sensor_data))
        query = f"INSERT INTO sensor_data ({columns}) VALUES ({values})"
        
        cur.execute(query, list(sensor_data.values()))
        conn.commit()

        print("Data sent to database:", sensor_data)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Run the function
send_data()
