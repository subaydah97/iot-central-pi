import time
import json
import random
import paho.mqtt.client as mqtt

# MQTT broker settings
broker = "localhost"   # Change if your broker is elsewhere
port = 1883
topic = "epc1522/data"

# Create MQTT client and connect
client = mqtt.Client()
client.connect(broker, port, 60)

print("Publishing fake sensor data to MQTT broker...")

try:
    while True:
        # Generate fake sensor data
        payload = {
            "temperature": round(random.uniform(18.0, 28.0), 2),
            "humidity": round(random.uniform(40.0, 60.0), 2),
            "gas": round(random.uniform(100, 500), 2),
            "magnetic_field": round(random.uniform(0.1, 1.0), 3),
            "door_open": random.choice([True, False]),
            "vibration": round(random.uniform(0, 5), 2),
            "voltage": round(random.uniform(220, 230), 1),
            "current": round(random.uniform(0.1, 1.5), 2)
        }

        # Convert to JSON string
        payload_str = json.dumps(payload)

        # Publish to MQTT topic
        client.publish(topic, payload_str)

        # Print to terminal
        print("Published:", payload_str)

        # Wait before sending next message
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopped publishing.")
    client.disconnect()
