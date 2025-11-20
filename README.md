# IIoT Hub – Edge & Central Architecture  

Dit project realiseert een industriële IIoT-hub bestaande uit een **Edge Processing Controller (EPC1522)** en een **centrale IoT-omgeving op een Raspberry Pi**. De infrastructuur verzamelt, verwerkt en visualiseert sensordata via MQTT, Node-RED, InfluxDB en Grafana.

## Architectuuroverzicht

- **EPC1522 (Edge Node)**
  - Draait **Node-RED** lokaal voor real-time monitoring van sensordata.
  - Ontvangt sensordata via **MQTT** (`bridge1522/data`) van aangesloten sensoren.
  - Voert **edge computing** uit:
    - Batching van numerieke sensordata (sensor 1: temperatuur, druk, luchtvochtigheid; sensor 2: voltage, stroom, vermogen) per minuut.
    - Detectie van kritische waarden en waarschuwingen lokaal.
    - Boolean sensoren (vibratie, magneetveld, deur, gas) worden onmiddellijk doorgestuurd bij detectie.
  - Stuurt verwerkte/batched data door naar de centrale omgeving via een **one-way MQTT-bridge** (`epc1522/data`).

- **Raspberry Pi (Central IoT Hub)**
  - Host de centrale **Mosquitto MQTT broker**, **InfluxDB** en **Grafana** dashboards.
  - Ontvangt **geaggregeerde/batched data** van EPC via de MQTT-bridge.
  - Node-RED op de Pi schrijft binnenkomende batches naar InfluxDB voor historisch inzicht.
  - Grafana visualiseert realtime en historische sensorgegevens, inclusief alerts voor kritische waarden.

## Dataflow

1. Sensor → **MQTT** → EPC → real-time monitoring in Node-RED.  
2. EPC verwerkt data lokaal (edge logic: batching, detectie kritische waarden).  
3. EPC → MQTT bridge → Raspberry Pi.  
4. Raspberry Pi → **InfluxDB** → historische opslag van batches.  
5. Grafana dashboard toont grafieken, status en alerts per sensor/paneel.

## Alerts & Panels

- **Sensor 1 (Temp, Pressure, Humidity):** alerts bij overschrijding kritische waarden.  
- **Sensor 2 (Voltage, Current, Power):** waarschuwing bij bijna kritische waarde, kritisch alert bij overschrijding.  
- **Sensor 3 & 4 (Vibration, Magnetic):** onmiddellijk alert bij detectie.  
- **Sensor 5 & 6 (Gas, Door):** onmiddellijk alert bij detectie; deuralerts ook na 30s/60s open.  
- Grafana panels kunnen meerdere boolean sensoren combineren (bijv. machine health panel voor sensor 3 & 4, environment panel voor sensor 5 & 6).

## Doel van de opdracht

- Lokale data-analyse en edge computing uitvoeren op de EPC vóór verzending.  
- Een betrouwbare en schaalbare IIoT-architectuur bouwen.  
- Data centraal opslaan, visualiseren en real-time alerts tonen.  
- Complete demonstratie en documentatie opleveren van de IIoT-keten.
