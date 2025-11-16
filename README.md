# IIoT Hub – Edge & Central Architecture  
Dit project realiseert een industriële IIoT-hub bestaande uit een **Edge Processing Controller (EPC1522)** en een **centrale IoT-omgeving op een Raspberry Pi**. De infrastructuur verzamelt, verwerkt en visualiseert sensordata via MQTT, Node-RED, InfluxDB en Grafana.

## Architectuuroverzicht
- **EPC1522 (Edge Node)**
  - Draait **Node-RED** lokaal.
  - Ontvangt sensordata via **MQTT** en voert **edge computing** uit (lokale berekeningen en beslislogica).
  - Stuurt relevante data door naar de centrale omgeving via een **MQTT-bridge**.

- **Raspberry Pi (Central IoT Hub)**
  - Host de centrale **Mosquitto MQTT broker**, **InfluxDB** en **Grafana** dashboards.
  - Node-RED op de Pi schrijft binnenkomende data naar InfluxDB voor historisch inzicht.
  - Grafana visualiseert realtime en historische sensorwaarden.

## Dataflow
1. Sensor → **MQTT** → EPC → uitlezen oo Node-RED
2. EPC verwerkt data lokaal (edge logic)  
3. EPC → MQTT bridge → Raspberry Pi  
4. Raspberry pi → **InfluxDB**  
5. Grafana dashboard toont grafieken en status  

## Doel van de opdracht
- Lokale data-analyse op de EPC uitvoeren vóór verzending.
- Een betrouwbare en schaalbare IIoT-architectuur bouwen.
- Data centraal opslaan en visualiseren.
- Een complete demonstratie + documentatie opleveren van de IIoT-keten.

---

