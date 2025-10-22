import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point

# ---------------- CONFIGURATION ----------------
INFLUX_URL = "http://172.20.10.3:8086"
INFLUX_TOKEN = "ezq1o5_qLRvPAVHbsAi6H6OS3O-Y5hSgc7fhEChRmQ5_MhsUbZbLfabK0hE2jPJcsxGol43mvC3YHS373sE-dw=="
INFLUX_ORG = "raspberrypi"
INFLUX_BUCKET = "epcdata"

MQTT_BROKER = "172.20.10.3"
MQTT_TOPIC = "bridge1522/data"
# ------------------------------------------------

# Store the latest values from all sensors
latest_data = {
    "temperature": None,
    "pressure": None,
    "humidity": None,
    "voltage": None,
    "current": None,
    "power": None,
    "vibration": False,
    "gasStatus": False,
    "magneticField": 0,
    "doorStatus": False
}

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

def write_to_influx():
    """Write the current snapshot to InfluxDB."""
    point = Point("sensor_data")
    
    # Floats
    for key in ["temperature", "pressure", "humidity",
                "voltage", "current", "power"]:
        if latest_data[key] is not None:
            point.field(key, float(latest_data[key]))
    
    # Integers
    point.field("magneticField", int(latest_data["magneticField"]))
    
    # Booleans
    for key in ["vibration", "gasStatus", "doorStatus"]:
        point.field(key, bool(latest_data[key]))
    
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"Wrote point: {latest_data}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        # Update only the keys present in the incoming message
        for key in data:
            latest_data[key] = data[key]
        
        # Write full snapshot every time a message arrives
        write_to_influx()
    except Exception as e:
        print(f"Error processing message: {e}")

# Connect to MQTT broker
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER)

# Subscribe and start listening
mqtt_client.subscribe(MQTT_TOPIC)
print(f"Listening for MQTT messages on {MQTT_TOPIC} ...")
mqtt_client.loop_forever()

