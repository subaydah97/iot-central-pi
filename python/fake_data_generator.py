import random
import time
from influxdb_client import InfluxDBClient, Point

# ---------------- CONFIGURATION ----------------
INFLUX_URL = "http://172.20.10.3:8086"
INFLUX_TOKEN = "ezq1o5_qLRvPAVHbsAi6H6OS3O-Y5hSgc7fhEChRmQ5_MhsUbZbLfabK0hE2jPJcsxGol43mvC3YHS373sE-dw=="
INFLUX_ORG = "raspberrypi"
INFLUX_BUCKET = "epcdata"
# ------------------------------------------------

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

while True:
    # Generate fake sensor data
    data = {
        "temperature": round(random.uniform(18.0, 25.0), 2),   # °C
        "pressure": round(random.uniform(101300, 101800), 2),  # Pa
        "humidity": round(random.uniform(40.0, 60.0), 2),      # %
        "voltage": round(random.uniform(215.0, 245.0), 4),     # V
        "current": round(random.uniform(1.0, 10.0), 3),        # A
        "power": round(random.uniform(100.0, 2000.0), 3),      # W
        # Boolean statuses
        "vibration": random.choice([True, False]),
        "gasStatus": random.choice([True, False]),
        "doorStatus": random.choice([True, False]),
        # Numeric magnetic field (e.g., 20–60 μT)
        "magneticField": random.randint(20, 60)
    }

    # Create an InfluxDB point
    point = Point("sensor_data")
    for key, value in data.items():
        point.field(key, value)

    # Write the point to InfluxDB
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    print(f"✅ Fake data written: {data}")
    time.sleep(5)
