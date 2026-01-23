import time
import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions

# -------------------
# MQTT Setup
# -------------------
BROKER = "localhost"
TOPIC_SUB = "bridge1522/data"
TOPIC_BATCH = "epc1522/batch"
TOPIC_ALERTS = "epc1522/alerts"

client = mqtt.Client(client_id="epc_edge")
client.connect(BROKER, 1883, 60)

# -------------------
# InfluxDB Setup
# -------------------
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "nE_KixsEz15BUwiYAnETYJW9dnJNixdPYOCU_VjPtu9LLdgc67X0NvEYq8eMnDRwTrDsy9AwT7MIiRbUbHgs8g=="
INFLUX_ORG = "iot_org"
INFLUX_BUCKET = "iot_bucket"

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

write_api = influx_client.write_api(
    write_options=WriteOptions(
        batch_size=1000,      # large enough to avoid early flush
        flush_interval=60000  # 60 seconds for numeric batching
    )
)

# -------------------
# Buffers for numeric sensors
# -------------------
buffers = {
    "temperature": [],
    "humidity": [],
    "pressure": [],
    "voltage": [],
    "current": [],
    "power": []
}

# -------------------
# Thresholds
# -------------------
THRESHOLDS = {
    "temperature": {"warn": 40.0, "crit": 45.0},
    "humidity": {"warn": 65.0, "crit": 70.0},
    "pressure": {"warn": 100000.0, "crit": 105000.0},
    "voltage": {"warn": 2.0, "crit": 0.5},
    "current": {"warn": 2.0, "crit": 0.2},
    "power": {"warn": 2.5, "crit": 0.5}
}

# -------------------
# Utility functions
# -------------------
def average(values):
    return sum(values) / len(values)

def send_alert(alert, severity):
    msg = {"alert": alert, "severity": severity, "timestamp": int(time.time())}
    client.publish(TOPIC_ALERTS, json.dumps(msg))
    print("[ALERT] Sent:", msg)

def write_numeric_batch(batch):
    for key, value in batch.items():
        if key == "timestamp":
            continue
        point = Point(key).field("value", value).time(batch["timestamp"], WritePrecision.S)
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print("[INFO] Numeric batch written:", batch)

def write_event_point(field, status):
    point = Point(field).field("value", int(status)).time(int(time.time()), WritePrecision.S)
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"[INFO] Event written: {field}={status}")

# -------------------
# Door state
# -------------------
door_open_time = None
door_alert_sent = False

# -------------------
# MQTT Callback
# -------------------
def on_message(client, userdata, msg):
    global door_open_time, door_alert_sent

    try:
        data = json.loads(msg.payload.decode())
    except Exception as e:
        print("[ERROR] JSON decode error:", e)
        return

    # --- Numeric sensors ---
    if "temperature" in data:
        buffers["temperature"].append(data["temperature"])
        buffers["humidity"].append(data["humidity"])
        buffers["pressure"].append(data["pressure"])

    if "voltage" in data:
        buffers["voltage"].append(data["voltage"])
        buffers["current"].append(data["current"])
        buffers["power"].append(data["power"])

    # --- Event sensors ---
    if "vibration" in data:
        write_event_point("vibration", data["vibration"])
        if data["vibration"]:
            send_alert("UNEXPECTED_VIBRATION", "CRITICAL")

    if "magneticField" in data:
        write_event_point("magneticField", data["magneticField"])
        if data["magneticField"]:
            send_alert("UNAUTHORIZED_ACCESS", "CRITICAL")

    if "gasStatus" in data:
        write_event_point("gasStatus", data["gasStatus"])
        if data["gasStatus"]:
            send_alert("GAS_LEAK_DETECTED", "CRITICAL")

    # --- Door logic ---
    if "doorStatus" in data:
        write_event_point("doorStatus", data["doorStatus"])
        if data["doorStatus"]:
            if door_open_time is None:
                door_open_time = time.time()
                door_alert_sent = False
            elif time.time() - door_open_time > 10 and not door_alert_sent:
                send_alert("DOOR_OPEN_TOO_LONG", "WARNING")
                door_alert_sent = True
        else:
            door_open_time = None
            door_alert_sent = False

# -------------------
# Start MQTT
# -------------------
client.on_message = on_message
client.subscribe(TOPIC_SUB)
client.loop_start()
print("[INFO] MQTT subscriber started. Listening to:", TOPIC_SUB)

# -------------------
# Batch loop for numeric sensors (every minute)
# -------------------
while True:
    time.sleep(60)
    batch = {"timestamp": int(time.time())}

    for key in buffers:
        if len(buffers[key]) > 0:
            avg = round(average(buffers[key]), 2)
            batch[key] = avg
            buffers[key].clear()

            warn = THRESHOLDS[key]["warn"]
            crit = THRESHOLDS[key]["crit"]

            # Warning alerts
            if ((key in ["temperature","humidity","pressure"] and avg >= warn) or
                (key in ["voltage","current","power"] and avg <= warn)):
                send_alert("POSSIBLE_POWER_OUTAGE" if key in ["voltage","current","power"] else f"POSSIBLE_{key.upper()}_ISSUE",
                           "WARNING")

            # Critical alerts
            if ((key in ["temperature","humidity","pressure"] and avg >= crit) or
                (key in ["voltage","current","power"] and avg <= crit)):
                send_alert("POWER_OUTAGE" if key in ["voltage","current","power"] else f"{key.upper()}_CRITICAL",
                           "CRITICAL")

    if len(batch) > 1:
        client.publish(TOPIC_BATCH, json.dumps(batch))
        write_numeric_batch(batch)
