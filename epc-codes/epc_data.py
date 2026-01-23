import time
import json
import random
import paho.mqtt.client as mqtt

# MQTT setup  Pi IP
BROKER = "10.10.10.1"  # IP van de Raspberry Pi
TOPIC_PUB = "bridge1522/data"

client = mqtt.Client(client_id="epc_dummy")
client.connect(BROKER, 1883, 60)

# Dummy data generator (all sensors every 10s)
def generate_sensor_data():
    return {
        "temperature": round(random.uniform(20.0, 50.0), 2),
        "pressure": round(random.uniform(99000, 103000), 2),
        "humidity": round(random.uniform(30.0, 80.0), 2),
        "voltage": round(random.uniform(0.0, 5.0), 3),
        "current": round(random.uniform(0.0, 5.0), 3),
        "power": round(random.uniform(0.0, 10.0), 3),
        "vibration": random.choice([True, False]),
        "gasStatus": random.choice([True, False]),
        "magneticField": random.choice([True, False]),
        "doorStatus": random.choice([True, False])
    }

# Main loop: publish every 10 seconds
while True:
    payload = generate_sensor_data()
    client.publish(TOPIC_PUB, json.dumps(payload))
    print("[PUBLISHED]", payload)
    time.sleep(10)