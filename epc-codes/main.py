import time
import json
import paho.mqtt.client as mqtt

# -------------------
# MQTT setup → Pi IP
# -------------------
BROKER = "10.10.10.1"
TOPIC_SUB = "bridge1522/data"
TOPIC_BATCH = "epc1522/batch"
TOPIC_ALERTS = "epc1522/alerts"

client = mqtt.Client(client_id="epc_edge")
client.connect(BROKER, 1883, 60)

# -------------------
# Buffers voor numeric sensors
# -------------------
buffers = {
    "temperature": [], "humidity": [], "pressure": [],
    "voltage": [], "current": [], "power": []
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
# Door state
# -------------------
door_open_time = None
door_alert_sent = False

# -------------------
# Helpers
# -------------------
def average(values):
    return sum(values) / len(values)

def send_alert(alert, severity):
    msg = {"alert": alert, "severity": severity, "timestamp": int(time.time())}
    client.publish(TOPIC_ALERTS, json.dumps(msg))
    print("[ALERT] Sent:", msg)

# -------------------
# MQTT callback
# -------------------
def on_message(client, userdata, msg):
    global door_open_time, door_alert_sent
    try:
        data = json.loads(msg.payload.decode())
    except:
        return

    # --- Numeric sensors ---
    for key in ["temperature", "humidity", "pressure"]:
        if key in data: buffers[key].append(data[key])
    for key in ["voltage", "current", "power"]:
        if key in data: buffers[key].append(data[key])

    # --- Event sensors ---
    if data.get("vibration"): send_alert("UNEXPECTED_VIBRATION", "CRITICAL")
    if data.get("magneticField"): send_alert("UNAUTHORIZED_ACCESS", "CRITICAL")
    if data.get("gasStatus"): send_alert("GAS_LEAK_DETECTED", "CRITICAL")

    # --- Door logic ---
    if "doorStatus" in data:
        status = data["doorStatus"]
        if status:
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
print("[INFO] EPC MQTT subscriber started. Listening to:", TOPIC_SUB)

# -------------------
# Batch loop voor numeric sensors (every 1 min)
# -------------------
while True:
    time.sleep(60)
    batch = {"timestamp": int(time.time())}
    for key in buffers:
        if buffers[key]:
            avg = round(average(buffers[key]), 2)
            batch[key] = avg
            buffers[key].clear()

            warn = THRESHOLDS[key]["warn"]
            crit = THRESHOLDS[key]["crit"]
            if ((key in ["temperature","humidity","pressure"] and avg >= warn) or
                (key in ["voltage","current","power"] and avg <= warn)):
                send_alert(
                    "POSSIBLE_POWER_OUTAGE" if key in ["voltage","current","power"] else f"POSSIBLE_{key.upper()}_ISSUE",
                    "WARNING"
                )
            if ((key in ["temperature","humidity","pressure"] and avg >= crit) or
                (key in ["voltage","current","power"] and avg <= crit)):
                send_alert(
                    "POWER_OUTAGE" if key in ["voltage","current","power"] else f"{key.upper()}_CRITICAL",
                    "CRITICAL"
                )

    if len(batch) > 1:
        client.publish(TOPIC_BATCH, json.dumps(batch))
        print("[BATCH PUBLISHED]", batch)