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
    for key in ["temperature", "pressure", "humidity", "voltage", "current", "power"]:
        val = latest_data[key]
        if val is not None:
            try:
                point.field(key, float(val))
            except (ValueError, TypeError):
                print(f"Skipping invalid float for {key}: {val}")

    # Integer
    try:
        point.field("magneticField", int(latest_data["magneticField"]))
    except (ValueError, TypeError):
        print(f"Invalid integer for magneticField: {latest_data['magneticField']}")

    # Booleans
    for key in ["vibration", "gasStatus", "doorStatus"]:
        point.field(key, bool(latest_data[key]))

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"Wrote to InfluxDB: {latest_data}")

def normalize_incoming_data(data):
    """Ensure data types are correct and handle missing/optional fields."""
    normalized = {}

    for key, value in data.items():
        if key in ["temperature", "pressure", "humidity", "voltage", "current", "power"]:
            try:
                normalized[key] = float(value)
            except (ValueError, TypeError):
                print(f"Invalid float for {key}: {value}")

        elif key == "magneticField":
            try:
                normalized[key] = int(value)
            except (ValueError, TypeError):
                print(f"Invalid integer for magneticField: {value}")

        elif key in ["vibration", "doorStatus", "gasStatus"]:
            if value is True:
                normalized[key] = True
            else:
                normalized[key] = False

        else:
            print(f"Unknown key received: {key}")

    return normalized

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8").strip()
        data = json.loads(payload)
        print(f"Received: {data}")

        normalized = normalize_incoming_data(data)

        # Update latest_data only for keys present
        for key, value in normalized.items():
            latest_data[key] = value

        # Write full snapshot each time
        write_to_influx()

    except json.JSONDecodeError:
        print(f"Invalid JSON received: {msg.payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Connect to MQTT broker
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

print(f"Connecting to MQTT broker at {MQTT_BROKER} ...")
mqtt_client.connect(MQTT_BROKER)

# Subscribe and start listening
mqtt_client.subscribe(MQTT_TOPIC)
print(f"Listening for MQTT messages on '{MQTT_TOPIC}' ...")

mqtt_client.loop_forever()
