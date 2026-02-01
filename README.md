# IIoT Hub – Edge & Central Architecture  

Dit project realiseert een industriële IIoT-hub bestaande uit een **Edge Processing Controller (EPC1522)** en een **centrale IoT-omgeving op een Raspberry Pi**. De infrastructuur verzamelt, verwerkt en visualiseert sensordata via **MQTT**, **Node-RED**, **InfluxDB** en **Grafana**.

## Architectuuroverzicht

- **EPC1522 (Edge Node)**
  - Ontvangt sensordata via **MQTT** (`bridge1522/data`) van aangesloten sensoren.
  - Voert **edge computing** uit:
    - **Batching** van numerieke sensordata (sensor 1: temperatuur, druk, luchtvochtigheid; sensor 2: voltage, stroom, vermogen) per minuut.
    - Detectie van kritische waarden en waarschuwingen lokaal.
    - Boolean sensoren (vibratie, magneetveld, deur, gas) worden **onmiddellijk doorgestuurd** bij detectie.
  - Stuurt verwerkte/batched data en alerts door naar de centrale omgeving via een **one-way MQTT-bridge**:
    - `epc1522/batch` → numerieke sensordata  
    - `epc1522/alerts` → boolean/event alerts
  - Draait optioneel **Node-RED lokaal** voor real-time monitoring van sensordata.

- **Raspberry Pi (Central IoT Hub)**
  - Host de centrale **Mosquitto MQTT broker**, **InfluxDB** en **Grafana dashboards**.
  - Ontvangt **geaggregeerde/batched data en alerts** van EPC via de MQTT-bridge.
  - Node-RED of Python-script schrijft binnenkomende **numerieke batches naar InfluxDB** voor historische opslag.
  - Event alerts worden ook opgeslagen in InfluxDB als **veld met waarde 1**, zodat Grafana alerts kan visualiseren.
  - Grafana visualiseert realtime en historische sensorgegevens, inclusief waarschuwingen en kritische alerts.

## Dataflow


1. **Sensor → MQTT → EPC**  
   Sensordata van alle sensoren komt binnen op de EPC via MQTT.

2. **EPC Edge Processing**  
   - Numerieke sensordata wordt gemiddeld en gebatched per minuut.  
   - Kritische waarden en waarschuwingen worden lokaal gedetecteerd.  
   - Boolean/event sensoren worden direct doorgestuurd bij detectie.

3. **EPC → Raspberry Pi (MQTT bridge)**  
   - `epc1522/batch` → gebatchte numerieke data  
   - `epc1522/alerts` → boolean/event alerts  

4. **Raspberry Pi → InfluxDB → Grafana**  
   - Historische opslag van numerieke batches.  
   - Alerts opgeslagen als afzonderlijke velden (1 = detectie).  
   - Grafana dashboards tonen grafieken, status en alerts per sensor/paneel.

## Alerts & Panels

- **Sensor 1 (Temp, Pressure, Humidity):** waarschuwing bij bijna kritische waarden; kritisch alert bij overschrijding.  
- **Sensor 2 (Voltage, Current, Power):** waarschuwing bij bijna kritische waarden; kritisch alert bij overschrijding.  
- **Sensor 3 & 4 (Vibration, Magnetic):** onmiddellijk alert bij detectie.  
- **Sensor 5 & 6 (Gas, Door):** onmiddellijk alert bij detectie; deur-alerts ook na 30s/60s open.  
- Grafana panels kunnen meerdere boolean sensoren combineren:
  - Machine Health panel (sensor 3 & 4)  
  - Environment panel (sensor 5 & 6)

## Doel van de opdracht

- Lokale data-analyse en **edge computing uitvoeren op de EPC** vóór verzending naar de centrale hub.  
- Een **betrouwbare en schaalbare IIoT-architectuur** bouwen met MQTT, InfluxDB en Grafana.  
- **Data centraal opslaan, visualiseren en real-time alerts tonen**.  
- **Complete demonstratie en documentatie opleveren** van de IIoT-keten.
