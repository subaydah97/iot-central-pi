import time
import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions

# -------------------
# MQTT Setup → listen to EPC
# -------------------
BROKER = "localhost"  # Pi itself
TOPIC_SUBS = [
    "bridge1522/data",
    "epc1522/batch",
    "epc1522/alerts"
]

client = mqtt.Client(client_id="influx_writer")
client.connect(BROKER, 1883, 60)

# -------------------
# InfluxDB Setup
# -------------------
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "nE_KixsEz15BUwiYAnETYJW9dnJNixdPYOCU_VjPtu9LLdgc67X0NvEYq8eMnDRwTrDsy9AwT7MIiRbUbHgs8g=="
INFLUX_ORG = "iot_org"
INFLUX_BUCKET = "iot_bucket"

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(
    write_options=WriteOptions(
        batch_size=1000,
        flush_interval=10000  # flush every 10s
    )
)

# -------------------
# Helper to write numeric batch
# -------------------
def write_numeric_batch(batch):
    ts = batch.get("timestamp", int(time.time()))
    for key, value in batch.items():
        if key == "timestamp":
            continue
        try:
            # Each sensor is its own measurement, field="value"
            point = Point(key).field("value", float(value)).time(ts, WritePrecision.S)
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        except Exception as e:
            print(f"[ERROR] Could not write numeric {key}={value}: {e}")
    print("[INFO] Numeric batch written:", batch)

# -------------------
# Helper to write event / alert points
# -------------------
def write_event_point(field, status):
    point = (
        Point(field)
        .field("value", int(status))
        .time(int(time.time()), WritePrecision.S)
    )

    write_api.write(
        bucket=INFLUX_BUCKET,
        org=INFLUX_ORG,
        record=point
    )

    print(f"[INFO] Event written: {field}={status}")

# -------------------
# MQTT Callback
# -------------------
def on_message(client, userdata, msg):
    topic = msg.topic

    try:
        data = json.loads(msg.payload.decode())
    except Exception as e:
        print("[ERROR] JSON decode error:", e)
        return

    if topic == "bridge1522/data":
        # Event sensors
        for field in ["vibration", "gasStatus", "magneticField", "doorStatus"]:
            if field in data:
                write_event_point(field, data[field])

    elif topic == "epc1522/batch":
        # Numeric sensors (averaged)
        write_numeric_batch(data)

    elif topic == "epc1522/alerts":
        # Alerts as events in Influx
        alert_name = data.get("alert", "UNKNOWN_ALERT")
        severity = data.get("severity", "INFO")
        write_event_point(f"ALERT_{alert_name}_{severity}", 1)

# -------------------
# Start MQTT
# -------------------
client.on_message = on_message

for topic in TOPIC_SUBS:
    client.subscribe(topic)

client.loop_start()

print("[INFO] Influx writer started. Listening to topics:", TOPIC_SUBS)

# -------------------
# Keep script running
# -------------------
while True:
    time.sleep(1)
