# Raspberry Pi 5 Setup Guide

## Overzicht
Deze handleiding beschrijft de volledige setup van de **Raspberry Pi 5** als **centrale IIoT-node** binnen het netwerk.

De Raspberry Pi:
- fungeert als **centrale MQTT broker**
- ontvangt data via een **MQTT bridge** vanaf de **EPC1522**
- slaat sensordata op in **InfluxDB**
- visualiseert data via **Grafana**
- kan aanvullende verwerking uitvoeren met **Python scripts**

> De Raspberry Pi vormt hiermee de **centrale data- en visualisatielaag** van de IIoT-opstelling.

---

## 1. Voorbereiding en Verbinding

### 1.1 Raspberry Pi OS flashen
Gebruik **Raspberry Pi Imager** om het OS te installeren.

1. Kies **Raspberry Pi OS (64-bit)**  
2. Stel via **Advanced Options** in:
   - Hostname (bijv. `raspberrypi`)
   - SSH → **Enable**
   - Gebruikersnaam + wachtwoord
3. Flash de SD-kaart

> Deze gebruikersnaam en het wachtwoord gebruik je later voor SSH.

---

### 1.2 Fysieke verbinding
Sluit aan:
- **Ethernet** → laptop (of netwerk)
- **Power** → Raspberry Pi

> De Raspberry Pi host daarnaast een **eigen Access Point**  
### -Aparte handleiding – raspberry_ap_setup.md.

---

## 2. Inloggen op de Raspberry Pi

Log in via SSH vanaf je laptop:

```bash
ssh <gebruikersnaam>@<raspberry_pi_ip>
```

## 3. Acces point services controlen
> Zorg dat het AP actief is: 

```bash
sudo systemctl start hostapd
sudo systemctl start dnsmasq
```

> Controleer of het AP actief is: 

```bash
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

> Systeem updaten: 

```bash
sudo apt update && sudo apt upgrade -y
```

## Docker & Docker Compose installeren

### 5.1 Docker installeren 

```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 5.2 Docker gebruiken zonder sudo

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 5.3 Docker Compose plugin

```bash
sudo apt install docker-compose-plugin -y
```
> Controleer met: 

```bash
docker --version
docker compose version
```

# 6. Projectstructuur aanmaken (voorbeeld)

```bash
mkdir -p ~/iot-stack/{mosquitto,influxdb,grafana}
mkdir -p ~/iot-stack/mosquitto/{config,data,log}
cd ~/iot-stack
```

# 7. Mosquitto configuraie 

> Maak het bestand aan:

```bash
nano mosquitto/config/mosquitto.conf
```

> Zie mosquitto.conf 
```bash
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

# 8. Gebruik van docker.compose.yml

> Maak het bestand aan: 

```bash
nano docker-compose.yml
```
> Example:

```bash
services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto
    restart: always
    ports:
      - "1883:1883"   # MQTT plain
      - "9001:9001"   # WebSocket (optioneel)
    volumes:
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
      - ./mosquitto/config:/mosquitto/config

  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: always
    ports:
      - "8086:8086"
    volumes:
      - ./influxdb/data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=yourpassword
      - DOCKER_INFLUXDB_INIT_ORG=iot_org
      - DOCKER_INFLUXDB_INIT_BUCKET=iot_bucket

  grafana:
    image: grafana/grafana-oss:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=yourpassword
      - GF_USERS_ALLOW_SIGN_UP=false

```
# 9. Containers starten

> Dit doe je met: 

```bash
docker compose up -d

```
> Controleren met: 

```bash
docker ps
```

# 10. MQTT lokaal testen (Raspberry Pi)

> Subscriber: 

```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "test/#" -v
```

> Publisher (nieuwe terminal tab)
```bash
docker exec -it mosquitto mosquitto_pub -h localhost -t test/hello -m "hello from raspberry pi"
```


# 11. MQTT bridge testen (EPC → Raspberry Pi)

> Wanneer de bridge op de EPC actief is voer uit:

```bash
docker exec -it mosquitto mosquitto_sub -h localhost -t "bridge1522/#" -v
```
Wanneer data zichtbaar is = actief

# InfluxDB setup

> Controleer of de container gestart is met: 

```bash
docker ps
```

### Open de influxdb browser met: 
```bash
http://<raspberry_pi_ip>:8086
```

> Initiele setup: 
- Organisation
- Bucket
- API Token (opslaan)

# 13. Grafana setup

> Controleer of de container gestart is met: 

```bash
docker ps
```
### Open de grafana browser met: 
```bash
http://<raspberry_pi_ip>:3000
```
> Initiele setup: 
- Login:
- user: admin
- password: admin

> Wachtwoord na inloggen is te veranderen.

- InfluxDB koppelen
- Data Sources → InfluxDB
- URL: http://influxdb:8086
- Token: InfluxDB token
- Organisation + Bucket


# 14. Python scripts (MQTT → InfluxDB)

> Installeer python libs met:

```bash
pip3 install paho-mqtt influxdb-client
```
> Run: final_mqtt_to_influx 
- Dit script:
- luistert naar bridge1522/#
- schrijft data naar InfluxDB

# Monitoring en debugging

### Voer dit uit in de terminal van de raspberry pi 5: 

> Luisteren naar alle data:

```bash
docker exec -it mosquitto mosquitto_sub -t "bridge1522/#" -v
```
> Luisteren naar batches:

```bash
docker exec -it mosquitto mosquitto_sub -t "epc1522/batch" -v
```
> Luisteren naar alerts: 

```bash
docker exec -it mosquitto mosquitto_sub -t "epc1522/alerts" -v
```

# 16 Eindresultaat 
- EPC1522 voert edge computing uit
- MQTT bridge stuurt data naar Raspberry Pi
- InfluxDB slaat data op
- Grafana visualiseert realtime & historisch
