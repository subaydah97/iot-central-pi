import time
import json
import random
import paho.mqtt.client as mqtt

# MQTT setup
BROKER = "localhost"
TOPIC_PUB = "bridge1522/data"

client = mqtt.Client(client_id="epc_dummy")
client.connect(BROKER, 1883, 60)

# Dummy data generator
def generate_sensor_data():
    data_list = []

    # --- Sensor 1: Temperature / Pressure / Humidity ---
    sensor1 = {
    "temperature": round(random.uniform(20.0, 50.0), 2),
    "pressure": round(random.uniform(99000, 103000), 2),
    "humidity": round(random.uniform(30.0, 80.0), 2)
    }
    data_list.append(sensor1)

    # --- Sensor 2: Voltage / Current / Power ---
    sensor2 = {
    "voltage": round(random.uniform(0.0, 5.0), 3),
    "current": round(random.uniform(0.0, 5.0), 3),
    "power": round(random.uniform(0.0, 10.0), 3)
    }
    data_list.append(sensor2)

    # --- Sensor 3: Vibration (boolean, 50% chance) ---
    if random.choice([True, False]):
        data_list.append({"vibration": True})

    # --- Sensor 4: Gas (boolean, 20% chance) ---
    if random.random() < 0.2:
        data_list.append({"gasStatus": True})

    # --- Sensor 5: Magnetic field (boolean, 10% chance) ---
    if random.random() < 0.1:
        data_list.append({"magneticField": True})

    # --- Sensor 6: Door status (boolean, 5% chance) ---
    if random.random() < 0.05:
        data_list.append({"doorStatus": True})

    return data_list


# Main loop: publish every 10 seconds
while True:
    sensor_payloads = generate_sensor_data()
    for payload in sensor_payloads:
        client.publish(TOPIC_PUB, json.dumps(payload))
        print("Published:", payload)

    time.sleep(10)