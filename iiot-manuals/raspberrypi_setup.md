# Raspberry Pi 5 Setup Guide

## Overzicht 
Deze handleiding beschrijft de setup van de **Raspberry Pi 5** als centrale MQTT-broker, datacollector en visualisatieserver.

De Raspberry Pi ontvangt data via **MQTT van de EPC1522** (edge node) en schrijft deze weg in een InfluxDB-database.
Grafana wordt gebruikt om deze data overzichtelijk te visualiseren via dashboards.

**De Raspberry Pi fungeert als central hub in het IIoT-netwerk.**
