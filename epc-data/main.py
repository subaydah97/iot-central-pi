import time
import json
import paho.mqtt.client as mqtt

# -------------------------------
# MQTT setup
# -------------------------------
BROKER = "localhost"          # EPC local broker
TOPIC_SUB = "bridge1522/data"
TOPIC_PUB = "epc1522/data"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# -------------------------------
# Buffers for batching numeric sensors
# -------------------------------
buffers = {
    "sensor1_temp": [],
    "sensor1_pressure": [],
    "sensor1_humidity": [],
    "sensor2_power": []
}

# -------------------------------
# MQTT callback
# -------------------------------
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except Exception as e:
        print("JSON decode error:", e)
        return

    # SENSOR 1: Temperature / Pressure / Humidity
    if "temperature" in data:
        buffers["sensor1_temp"].append(data["temperature"])
        buffers["sensor1_pressure"].append(data["pressure"])
        buffers["sensor1_humidity"].append(data["humidity"])

    # SENSOR 2: Voltage / Current / Power
    if "voltage" in data:
        buffers["sensor2_power"].append(data)

    # Boolean sensors (3-6) — just forward as is (optional)
    boolean_keys = ["vibration", "magneticField", "gasStatus", "doorStatus"]
    if any(k in data for k in boolean_keys):
        client.publish(TOPIC_PUB, json.dumps(data))

# -------------------------------
# Start MQTT subscription
# -------------------------------
client.on_message = on_message
client.subscribe(TOPIC_SUB)
client.loop_start()

# -------------------------------
# Main loop: batch processing every 1 minute
# -------------------------------
BATCH_INTERVAL = 60  # seconds

while True:
    time.sleep(BATCH_INTERVAL)

    # SENSOR 1: batch
    for key in ["sensor1_temp", "sensor1_pressure", "sensor1_humidity"]:
        if buffers[key]:
            batch_data = buffers[key].copy()
            buffers[key].clear()
            client.publish(TOPIC_PUB, json.dumps({key: batch_data}))

    # SENSOR 2: batch
    if buffers["sensor2_power"]:
        batch = buffers["sensor2_power"].copy()
        buffers["sensor2_power"].clear()
        client.publish(TOPIC_PUB, json.dumps({"sensor2_power_batch": batch}))
