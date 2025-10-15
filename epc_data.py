import json
import time
import random
import paho.mqtt.client as mqtt

broker = "172.20.10.3"
topic = "epc1522/data"

client = mqtt.Client()
client.connect(broker, 1883, 60)

while True:
    data = {
        "temperature": round(random.uniform(20, 30), 1),
        "humidity": round(random.uniform(40, 60), 1),
        "pressure": round(random.uniform(1000, 1020), 1),
    }
    client.publish(topic, json.dumps(data))
    print("Published:", json.dumps(data))
    time.sleep(5)
