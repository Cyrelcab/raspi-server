import os
import json
import asyncio
from dotenv import load_dotenv
from ably import AblyRest

# Load environment variables (if using .env file)
load_dotenv()
API_KEY = os.getenv("ABLY_API_KEY")  # Replace with your actual key if not using .env

async def publish_data():
    # Initialize Ably client
    ably = AblyRest(API_KEY)
    channel = ably.channels.get("raspi-channel")

    # Create a sample JSON payload
    sensor_data = {
        "flow_rate_1": 3.5,
        "flow_rate_2": 4.2,
        "humidity_1": 65,
        "humidity_2": 70,
        "water_level_1": 2.3,
        "water_level_2": 2.8
    }

    # Convert dictionary to JSON string
    json_payload = json.dumps(sensor_data)

    # Publish JSON data to Ably channel
    await channel.publish("sensor_data", json_payload)

    print("JSON data sent to Ably:", json_payload)

# Run the async function
asyncio.run(publish_data())
