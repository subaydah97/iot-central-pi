# EPC1522 Setup Guide

##  Overzicht
Deze handleiding beschrijft de volledige setup van de **Edge PC (EPC1522)** die sensordata publiceert via een lokale **Mosquitto broker** en deze data doorstuurt naar de **Raspberry Pi broker** via een MQTT bridge.

De EPC fungeert als een **edge node** binnen het IIoT-netwerk en genereert dummy-sensordata met een Python-script in een Docker-container.

---

##  1. Voorbereiding en Verbinding

### 1.1 Fysieke verbinding
Verbind de **EPC1522** via een **Ethernet-kabel** met:
- je **laptop**, of  
- een **lokaal netwerk** waarin ook de **Raspberry Pi** aanwezig is.

>  Tip: gebruik bij voorkeur een directe bekabelde verbinding voor stabiele communicatie en lagere latentie.

---

### 1.2 Controleer de EPC-status via PLCnext
Voordat je met de installatie begint, moet je bevestigen dat de EPC correct online is.

1. Open de **PLCnext Store** of **PLCnext Engineer**.
2. Controleer of je EPC1522 zichtbaar is in het netwerk.
3. Controleer de **statusindicator**:
   -  *Online*: je kunt verder met de setup.  
   -  *Offline*: controleer de netwerkkabel, IP-instellingen of firewall.

> De status is eenvoudig te verifiëren in **PLCnext Store → Device Management**.  
> Zodra de EPC “Online” weergeeft, kun je verdergaan met de volgende stap.

---

## ⚙️ 2. Systeemvereisten

| Component | Beschrijving |
|------------|--------------|
| OS | Ubuntu / Debian (gebruikt op EPC1522) |
| Portainer | Containerbeheer via webinterface |
| Docker | Wordt automatisch geïnstalleerd met Portainer |
| Mosquitto | MQTT broker container |
| Python + paho-mqtt | Voor publishing tests scripts |

---

##  3. Toegang tot de EPC1522 via SSH

### 3.1 IP-adres vinden
Het IP-adres van de EPC1522 kan op verschillende manieren worden achterhaald:

-  **Optie 1 — Via Wireshark:**  
  Sluit je laptop aan op dezelfde netwerkpoort als de EPC1522.  
  Start **Wireshark** en filter op `bootp` of `dhcp`.  
  Zodra de EPC verbinding maakt, zie je een DHCP-request met het IP-adres in het pakketdetail.

-  **Optie 2 — Via Router of DHCP-server:**  
  Als de EPC is aangesloten op een netwerk met DHCP, kun je in het routerdashboard het toegewezen IP-adres terugvinden.

>  Noteer het gevonden IP-adres — dit heb je nodig om in te loggen via SSH.

---

### 3.2 Inloggen via SSH
Gebruik onderstaand commando om verbinding te maken met de EPC1522:

```bash
ssh admin@<ip-adres>
