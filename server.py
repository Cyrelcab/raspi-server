import os
import psycopg2
import serial
import time
import re

DB_URL = "postgresql://postgres.tsiiblalobzwtzcxuzck:flood-alert-system@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def send_data():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(DB_URL)
        print("Database connected")
        cur = conn.cursor()

        # Configure serial connection for GSM module
        ser = serial.Serial('/dev/serial0', 9600, timeout=1)

        # Set GSM module to Text Mode
        ser.write(b'AT+CMGF=1\r\n')
        time.sleep(1)

        # Initialize sensor data storage and flags
        sensor_data = {
            "phone_1": {"flow_rate_1": None, "humidity_1": None, "water_level_1": None},
            "phone_2": {"flow_rate_2": None, "humidity_2": None, "water_level_2": None},
        }
        received_data = {"phone_1": False, "phone_2": False}

        while True:
            ser.write(b'AT+CMGL="ALL"\r\n')
            time.sleep(1)
            response = ser.readlines()

            for line in response:
                message = line.decode('utf-8', errors="ignore").strip()

                if message.startswith("+CMGL:"):
                    message_index = message.split(',')[0].split(':')[1].strip()

                    ser.write(f'AT+CMGR={message_index}\r\n'.encode())
                    time.sleep(1)
                    sms_content = ser.readlines()

                    message_body = ""
                    for line in sms_content:
                        decoded_line = line.decode('utf-8', errors="ignore").strip()
                        if decoded_line and not decoded_line.startswith(("AT+CMGR", "OK")):
                            message_body += decoded_line

                    message_body = re.sub(r'\+CMGR: .*?,".*?",.*?,".*?"', "", message_body).strip()
                    print(f"Raw SMS: {message_body}")

                    try:
                        if ": " in message_body:
                            phone, data = message_body.split(": ", 1)
                            parts = data.split(", ")

                            if len(parts) == 3:
                                humidity = float(parts[0].split(": ")[1].replace("%", ""))
                                water_level = float(parts[1].split(": ")[1].replace("cm", ""))
                                flow_rate = float(parts[2].split(": ")[1].replace("L/s", ""))

                                if phone == "+639307077761":  # Phone 1
                                    sensor_data["phone_1"] = {
                                        "flow_rate_1": flow_rate,
                                        "humidity_1": humidity,
                                        "water_level_1": water_level,
                                    }
                                    received_data["phone_1"] = True

                                elif phone == "+639307077762":  # Phone 2
                                    sensor_data["phone_2"] = {
                                        "flow_rate_2": flow_rate,
                                        "humidity_2": humidity,
                                        "water_level_2": water_level,
                                    }
                                    received_data["phone_2"] = True

                    except Exception as e:
                        print(f"Error parsing SMS content: {e}")
                        continue

                    ser.write(f'AT+CMGD={message_index}\r\n'.encode())
                    time.sleep(1)

                    os.system('clear')

            # Check if both numbers have reported before storing
            if all(received_data.values()):
                query = """
                    INSERT INTO sensor_data (
                        flow_rate_1, humidity_1, water_level_1,
                        flow_rate_2, humidity_2, water_level_2
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    sensor_data["phone_1"]["flow_rate_1"], sensor_data["phone_1"]["humidity_1"], sensor_data["phone_1"]["water_level_1"],
                    sensor_data["phone_2"]["flow_rate_2"], sensor_data["phone_2"]["humidity_2"], sensor_data["phone_2"]["water_level_2"]
                )
                cur.execute(query, values)
                conn.commit()

                print("Data stored in database:", sensor_data)

                # Reset data after insertion
                sensor_data = {
                    "phone_1": {"flow_rate_1": None, "humidity_1": None, "water_level_1": None},
                    "phone_2": {"flow_rate_2": None, "humidity_2": None, "water_level_2": None},
                }
                received_data = {"phone_1": False, "phone_2": False}

            time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

send_data()
