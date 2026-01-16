import time
import json
import paho.mqtt.client as mqtt

# MQTT setup
BROKER = "localhost"
TOPIC_SUB = "bridge1522/data"

TOPIC_BATCH = "epc1522/batch"
TOPIC_ALERTS = "epc1522/alerts"

client = mqtt.Client(client_id="epc_edge")
client.connect(BROKER, 1883, 60)

# Buffers (6 values = 1 minute)
buffers = {
    "temperature": [],
    "humidity": [],
    "pressure": [],
    "voltage": [],
    "current": [],
    "power": []
}

# Thresholds
THRESHOLDS = {
    "temperature": {"warn": 40.0, "crit": 45.0},
    "humidity": {"warn": 65.0, "crit": 70.0},
    "pressure": {"warn": 100000.0, "crit": 105000.0},
    "voltage": {"warn": 2.0, "crit": 0.5},
    "current": {"warn": 2.0, "crit": 0.2},
    "power": {"warn": 2.5, "crit": 0.5}
}

# Utility
def average(values):
    return sum(values) / len(values)

def send_alert(alert, severity):
    client.publish(TOPIC_ALERTS, json.dumps({
        "alert": alert,
        "severity": severity,
        "timestamp": int(time.time())
    }))

# Door state
door_open_time = None
door_alert_sent = False   # <<< ADDED

# MQTT callback
def on_message(client, userdata, msg):
    global door_open_time, door_alert_sent

    try:
        data = json.loads(msg.payload.decode())
    except Exception as e:
        print("JSON decode error:", e)
        return

    # ---------- Sensor 1 ----------
    if "temperature" in data:
        buffers["temperature"].append(data["temperature"])
        buffers["humidity"].append(data["humidity"])
        buffers["pressure"].append(data["pressure"])

    # ---------- Sensor 2 ----------
    if "voltage" in data:
        buffers["voltage"].append(data["voltage"])
        buffers["current"].append(data["current"])
        buffers["power"].append(data["power"])

    # ---------- Event sensors ----------
    if data.get("vibration"):
        send_alert("UNEXPECTED_VIBRATION", "CRITICAL")

    if data.get("magneticField"):
        send_alert("UNAUTHORIZED_ACCESS", "CRITICAL")

    if data.get("gasStatus"):
        send_alert("GAS_LEAK_DETECTED", "CRITICAL")

    # ---------- Door logic (ANTI-SPAM) ----------
    if "doorStatus" in data:
        if data["doorStatus"] is True:
            if door_open_time is None:
                door_open_time = time.time()
                door_alert_sent = False
            elif time.time() - door_open_time > 10 and not door_alert_sent:
                send_alert("DOOR_OPEN_TOO_LONG", "WARNING")
                door_alert_sent = True
        else:
            door_open_time = None
            door_alert_sent = False


# Start MQTT
client.on_message = on_message
client.subscribe(TOPIC_SUB)
client.loop_start()

# Batch loop (1 minute)
while True:
    time.sleep(60)

    batch = {"timestamp": int(time.time())}

    for key in buffers:
        if len(buffers[key]) >= 6:
            avg = round(average(buffers[key]), 2)
            batch[key] = avg
            buffers[key].clear()

            warn = THRESHOLDS[key]["warn"]
            crit = THRESHOLDS[key]["crit"]

            if warn and (
                (key in ["temperature", "humidity", "pressure"] and avg >= warn) or
                (key in ["voltage", "current", "power"] and avg <= warn)
            ):
                send_alert(
                    "POSSIBLE_POWER_OUTAGE" if key in ["voltage", "current", "power"]
                    else f"POSSIBLE_{key.upper()}_ISSUE",
                    "WARNING"
                )

            if crit and (
                (key in ["temperature", "humidity", "pressure"] and avg >= crit) or
                (key in ["voltage", "current", "power"] and avg <= crit)
            ):
                send_alert(
                    "POWER_OUTAGE" if key in ["voltage", "current", "power"]
                    else f"{key.upper()}_CRITICAL",
                    "CRITICAL"
                )

    if len(batch) > 1:
        client.publish(TOPIC_BATCH, json.dumps(batch))

        print("Published batch:", batch)

