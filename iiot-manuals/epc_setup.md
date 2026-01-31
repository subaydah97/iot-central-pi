# EPC1522 Setup Guide

##  Overzicht
Deze handleiding beschrijft de volledige setup van de **Edge PC (EPC1522)** binnen een IIoT-netwerk.  
De EPC ontvangt **sensordata via MQTT** en verwerkt deze lokaal in een **docker-container**.

De binnenkomende data wordt vervolgens via een **MQTT bridge** doorgestuurd naar de **Raspberry Pi broker** voor centrale verwerking.  
Daarnaast wordt de data met behulp van een **Python-script** opgeslagen in een **time-series database (InfluxDB)** voor verdere analyse en visualisatie.

> De EPC functioneert dus als een **edge node** die zowel MQTT-verkeer verwerkt als data doorstuurt naar hogere lagen in het netwerk.

---

## 1. Voorbereiding en Verbinding

### 1.1 Fysieke verbinding
Verbind de **EPC1522** via een **Ethernet-kabel** met:
- je **laptop**, of  
- een **lokaal netwerk** waarin ook de **Raspberry Pi** aanwezig is.

>  *Tip:* gebruik bij voorkeur een directe bekabelde verbinding voor stabiele communicatie. 

---

### 1.2 Controleer de EPC-status
Voordat je met de installatie begint, moet je bevestigen dat de EPC correct online is.

1. Open de **PLCnext Store**.  
2. Controleer of je EPC1522 zichtbaar is in het netwerk.  
3. Controleer de **status**:
> De status is eenvoudig te verifiëren in **PLCnext Store → Device Management**.  
   -  *Offline*: controleer de netwerkkabel, IP-instellingen of firewall.
   -  *Online*: je kunt verder met de setup.

---

##  2. Systeemvereisten

| Component | Platform | Beschrijving |
|------------|-----------|---------------|
| **macOS** | Laptop / Werkstation | Wordt gebruikt voor configuratie, SSH-toegang en beheer van de EPC1522 via PLCnext Store en Terminal. |
| **EPC1522 (Edge PC)** | Ubuntu / Debian (PLCnext Linux) | Hoofdapparaat waarop Docker, Portainer en Mosquitto containers draaien. |
| **Portainer** | EPC1522 | Webinterface voor het beheren van Docker-containers. |
| **Docker** | EPC1522 | Container-engine die nodig is om Mosquitto en Python-scripts te draaien. |
| **Mosquitto** | EPC1522 | MQTT broker-container die data ontvangt en via bridging doorstuurt naar de Raspberry Pi. |
| **Python + paho-mqtt** | EPC1522 | Voor het uitvoeren van scripts die MQTT-data publiceren of verwerken. |

> **Opmerking:**  
> Je voert alle configuratie- en beheerstappen uit vanaf je **Laptop** (via SSH),  
> maar alle containers draaien lokaal op de **EPC1522**.


## 3. Toegang tot de EPC1522 via SSH

### 3.1 IP-adres vinden
Het IP-adres van de EPC1522 kan op verschillende manieren worden achterhaald:

- **Optie 1 — Via Wireshark:**  
  Sluit je laptop aan op dezelfde netwerkpoort als de EPC1522.  
  Start **Wireshark** en filter op `bootp` of `dhcp`.  
  Zodra de EPC verbinding maakt, zie je een DHCP-request met het IP-adres in het pakketdetails (management adress).

- **Optie 2 — Via Router of DHCP-server:**  
  Als de EPC is aangesloten op een netwerk met DHCP, kun je in het routerdashboard het toegewezen IP-adres terugvinden.

>  Noteer het gevonden IP-adres — dit heb je nodig om in te loggen via SSH.

---

### 3.2 Inloggen via SSH
Gebruik onderstaand commando om verbinding te maken met de EPC1522:

```bash
ssh admin@<ip-adres>
```
# 4. Installatie van Portainer

### 4.1 Update het systeem
Zorg dat alle pakketten up-to-date zijn:
```bash
sudo apt update && sudo apt upgrade -y
```
Ga naar de PLC Next Store, hier kan je de zoekfunctie gebruiken om portainer te installeren.

### 4.2 Toegang tot de Portainer UI
Open je browser en ga naar de UI via:

```bash
http://<ip-adres>:9000
```
Voltooi de initiële setup door een admin-account aan te maken.
>  *Tip:* maak een dummy_container aan in de UI (of ssh) voor testen. 

# 5. Installatie van Mosquitto MQTT Broker

Nu Portainer draait en Docker beschikbaar is via SSH, kunnen we de Mosquitto MQTT broker installeren en starten als container.

---

### 5.1 Mappenstructuur aanmaken
Maak eerst de benodigde mappen voor configuratie, data en logs:

```bash
mkdir -p ~/mosquitto/config ~/mosquitto/data ~/mosquitto/log
```
### 5.2 Configuratiebestand aanmaken
Maak een basisconfiguratie voor Mosquitto:

```bash
nano ~/mosquitto/config/mosquitto.conf
```
Voeg het volgende toe: 
```bash
# === Lokale broker-instellingen ===
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/

# === Logging ===
log_dest file /mosquitto/log/mosquitto.log

# lokaal topic
topic bridge1522/data out 0
```
> Opslaan met CTRL + O, afsluiten met CTRL + X.
> 
### 5.3 mosquitto container starten 
Start de Mosquitto broker als Docker-container:

```bash
docker run -d \
  --name mosquitto \
  --restart=always \
  -p 1883:1883 \
  -v ~/mosquitto/config:/mosquitto/config \
  -v ~/mosquitto/data:/mosquitto/data \
  -v ~/mosquitto/log:/mosquitto/log \
  eclipse-mosquitto
```
Docker herstart de container automatisch, maar blijft alle data behouden.
Controleer of de container draait met: 

```bash
docker ps
```
Controleer of mosquitto correct is gestart door de logs te bekijken.
```bash
docker logs mosquitto
```
Als er geen verbinding is controleer de poort verbinding met: 
```bash
sudo netstat -tulnp | grep 1883
```
Als je niets ziet controleer dan het config bestand. 

> **Opmerking:**  
> Omdat dit een lokale setup is, zie je alleen standaard startup-meldingen in de logs. Alles wat je nu publiceert op het topic **bridge1522/data** zal lokaal beschikbaar zijn voor testing.
Eventuele bridge-instellingen komen later wanneer de Raspberry Pi ook is ingesteld
### 5.4 epc_net netwerk

> Zorg ervoor dat de mosquitto container en eventuele test container op hetzelfde epc netwerk staan zodat de containers elkaar via naam kunnen vinden en direct met elkaar kunnen communiceren zonder IP-adressen te hoeven gebruiken.

Je maakt een (epc) netwerk aan met: 
```bash
docker network create epc_net
```
Controleer of het netwerk is aangemaakt met: 
```bash
docker network ls
```
Verbind de mosquitto en test container met het epc_net netwerk met: 
```bash
docker network connect epc_net mosquitto
```
```bash
docker network connect epc_net dummy_container # dit is een test container waarmee je later dummy data kan laten genereren en mqtt communicatie kan testen. 
```
Controleer de verbinding met: 
```bash
docker inspect mosquitto | grep -A5 "Networks"
```
---
### 6.1 Controleer of Python al geïnstalleerd is
```bash
python3 --version
```
Als er iets als Python 3.x.x verschijnt, is Python al aanwezig.

Als het commando niet werkt, moet je Python installeren.

### 6.2 Python installeren

Op een Debian/Ubuntu-gebaseerd systeem zoals de EPC1522 doe je dit:
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```
 Controleer nog eens of Python geïnstalleerd is met : 
```bash
python3 --version
```
> python3 → de Python runtime

python3-pip → package manager om extra libraries te installeren (zoals paho-mqtt)
### 6.3. Controleer de pip
```bash
pip3 --version
```
Als dit werkt, kun je nu alle benodigde Python-pakketten installeren

### 6.4 Vereiste Python-pakketten installeren
Installeer de MQTT client bibliotheek:

```bash
pip3 install paho-mqtt
```

# 7. MQTT lokaal testen en productie-topic

Nu Mosquitto draait op de EPC, kun je lokaal testen of de broker berichten ontvangt en publiceert.


### 7.1 Dummy data publiceren (optioneel) 

### **Optie 1: Via Portainer UI terminal**

1. Open **Portainer** in je browser (http://<EPC-ip>:9000).:  

2. Ga naar **Containers** en klik op **dummy_container**.  
3. Klik op **Console** of **Exec Console** (afhankelijk van je Portainer-versie).  
4. Kies `/bin/bash` of `/bin/sh` als shell.  
5. Je hebt nu een terminalsessie binnen de container.  
6. Maak de Python-scripts direct aan met `nano` of `vi`:  

```bash
nano mqtt_test_pub.py
```

Bijvoorbeeld: ***mqtt_test_pub.py***
```python
import time
import paho.mqtt.client as mqtt
import random

# Verbinden met de lokale Mosquitto broker
client = mqtt.Client()
client.connect("mosquitto", 1883, 60)

# Dummy data publiceren
while True:
    value = random.randint(0, 100)
    client.publish("bridge1522/data", value)
    print(f"Verzonden: {value}")
    time.sleep(2)  # iedere 2 seconden
```
Start het script in een terminal tab met:
```bash
python3 mqtt_test_pub.py
```
### 7.2 Dummy subscriber starten
Om te controleren of de berichten aankomen, open een tweede terminal tab op de EPC1522 en maak een subscriber script aan, bijvoorbeeld ***mqtt_test_sub.py***

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Ontvangen: {msg.topic} {msg.payload.decode()}")

client = mqtt.Client()
client.connect("mosquitto", 1883, 60)
client.subscribe("#")  # abonneer op alle topics
client.on_message = on_message
client.loop_forever()
```
Start de subscriber met: 
```bash 
python3 mqtt_test_sub.py
```
### lokaal testen
Als alles correct werkt, zie je in de subscriber-terminal de berichten verschijnen die door de publisher worden gestuurd:
```bash 
Ontvangen: bridge1522/data 42
Ontvangen: bridge1522/data 17
...
```
Hiermee weet je dat de lokaal draaiende Mosquitto broker berichten kan ontvangen en publiceren.

**Samengevat: Je hebt nu een Mosquitto broker en een dummy_container draaiend op de EPC1522, volledig lokaal. De broker is klaar om berichten te ontvangen en te publiceren.
> **Opmerking:**  
> Volg de raspberrypi_setup.md tot en met stap 10 om vervolgens verder te gaan met het testen van de bridge voor communicatie tussen de epc1522 en de Raspberry Pi 5
---
# 8. bridge tussen 2 brokers

### 8.1 navigeer naar de mosquitto.config file

Deze is eerder aangemaakt je komt hier met: 
```bash
nano ~/mosquitto/config/mosquitto.conf
```

### 8.2 Pas de configuratie aan voor bridging

```bash
listener 8883
allow_anonymous false
password_file /mosquitto/config/passwd

connection bridge_to_pi
address 10.10.10.1:1883

#  Ruwe data NIET doorsturen
# topic bridge1522/# out

#  Alleen gebatchte data naar Raspberry Pi
topic epc1522/batch out

# (optioneel) commando’s of config terug van Pi
topic epc1522/cmd in

start_type automatic
notifications false
try_private false
```
> Opslaan met CTRL + O, afsluiten met CTRL + X.

### 8.3 mosquitto container herstarten 

Je kan de mosquitto container herstarten met: 

```bash
docker restart mosquitto
```
>Hiermee wordt de bridge actief en kan de EPC1522 nu berichten doorsturen naar de Raspberry Pi broker en eventueel terug ontvangen.

Controleer of de bridge actief is met: 
```bash
docker logs mosquitto
```
> Of controleer of the bridge met de raspberry pi actied is met de installatie van Node red

- MQTT-in nodes tonen inkomende berichten van de EPC
- MQTT-out nodes kunnen testcommando’s terugsturen
- Dit is vooral handig voor debugging tijdens de ontwikkelfase.

# 9 Python scripts uitvoeren voor edge computing 


De EPC1522 kan edge computing uitvoeren met de Python scripts die in de repository zijn opgenomen, zoals:
#### main.py: edge computing logica 
#### epc_data.py:  generen van data om edge computing te testen. 

**Opmerking** Volg hierna de raspberrypi_setup.md verder

