# Raspberry Pi 5 – Access Point (AP) Setup Guide

Deze handleiding beschrijft stap voor stap hoe de **Raspberry Pi 5** wordt ingericht als **Wi‑Fi Access Point (AP)**, met **NAT**, zodat aangesloten apparaten internet hebben via **Ethernet**.

Daarnaast wordt uitgelegd hoe deze setup samenwerkt met de **EPC1522** en een **MQTT broker**.

---

## Overzicht

* Raspberry Pi 5 draait als **Wi‑Fi Access Point**
* Ethernet wordt gebruikt als **uplink naar internet**
* Wi‑Fi clients krijgen IP-adressen via **dnsmasq**
* Verkeer wordt gerouteerd via **NAT (iptables)**
* MQTT-communicatie tussen **EPC1522 ↔ Raspberry Pi** werkt via het AP-netwerk

**Netwerkvoorbeeld:**

```
Clients → WiFi (AP) → Raspberry Pi → Ethernet → Laptop/Internet
```

---

## 1. Inloggen via Ethernet

Tijdens de setup log je **via Ethernet** in (bijv. met Internet Sharing):

```bash
ssh your_userh@<your_raspi_ip>
```

---

## 2. Static IP configuratie (dhcpcd)

Open het configuratiebestand:

```bash
sudo nano /etc/dhcpcd.conf
```

Voeg toe:

```conf
# Static IP for Ethernet
interface eth0
static ip_address=your_raspi_ip/24

# Static IP example for Wi-Fi AP 
interface wlan0
static ip_address=10.10.10.1/24 
nohook wpa_supplicant
```

---

## 3. hostapd – Wi‑Fi Access Point

### 3.1 Configuratiebestand

```bash
sudo nano /etc/hostapd/hostapd.conf
```

```conf
interface=wlan0
driver=nl80211
ssid=yourssid
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
auth_algs=1
ignore_broadcast_ssid=0
country_code=NL
wpa=2
wpa_passphrase=yourpassword
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
```

### 3.2 hostapd default file

```bash
sudo nano /etc/default/hostapd
```

```conf
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

---

## 4. dnsmasq – DHCP server example

Backup eerst het originele bestand:

```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
```

Maak een nieuw configuratiebestand:

```bash
sudo nano /etc/dnsmasq.conf
```

```conf
interface=wlan0
dhcp-range=10.10.10.10,10.10.10.200,255.255.255.0,24h
dhcp-option=3,10.10.10.1
dhcp-option=6,10.10.10.1
server=8.8.8.8
bind-interfaces
```

---

## 5. IP Forwarding inschakelen

```bash
sudo nano /etc/sysctl.conf
```

Zorg dat deze regel actief is:

```conf
net.ipv4.ip_forward=1
```

Toepassen:

```bash
sudo sysctl -p
```

---

## 6. NAT configuratie (iptables)

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
```

Persistente opslag:

```bash
sudo apt install iptables-persistent -y
```

---

## 7. Services starten

```bash
sudo systemctl start hostapd
sudo systemctl start dnsmasq
```

Controleer status:

```bash
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

---

## 8. Test: Internet via AP

Verbind een telefoon of laptop met de Wi‑Fi **your_ssid**.

Test:

```bash
ping google.com
```

Als dit werkt:

AP werkt
NAT werkt
Internet beschikbaar

---

## 9. Inloggen via AP (zonder Ethernet)

Zodra de Pi opnieuw is opgestart:

```bash
ssh subaydahfarah@10.10.10.1
```

---

## 10. Architectuur – belangrijke observatie

* De Raspberry Pi **is** het netwerk wanneer hij als AP draait
* EPC en Pi moeten in **hetzelfde subnet** zitten
* In deze setup is dat: `10.10.10.0/24`

 Dit werkt zonder extra microcontroller

---

## Resultaat

Raspberry Pi 5 functioneert als Wi‑Fi Access Point
Clients hebben internet via NAT


