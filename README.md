# Real-World-Prototype-Codes

This repository contains prototype codes that demonstrate how Arduino Opta PLC, Raspberry Pi, and Blockchain can work together in real-world IoT and supply chain contexts.
The focus is on reliable data collection, secure communication (via Modbus TCP), and blockchain anchoring of sensor data for tamper-proof Digital Product Passports (DPP).

# Code Walkthrough
### 1. Arduino Opta (Modbus Client – .ino)

This sketch configures the Arduino Opta PLC to act as a Modbus TCP client. It communicates with a Raspberry Pi acting as a Modbus server.

Uses the ArduinoModbus and Ethernet libraries in Aeduino IDE.

Establishes static IPs for both Opta (192.168.60.2) and Pi (192.168.60.1).<br><br>
<img width="300" height="300" alt="Untitled diagram _ Mermaid Chart-2025-08-17-123353" src="https://github.com/user-attachments/assets/a57fee14-1c27-495b-b3bf-eba5675983c4" />



Polls three Modbus Holding Registers every second:

HR0: sensor voltage (mV → V)

HR1: sensor resistance Rs (kΩ)

HR2: normalized Rs/R0 ratio

It avoids small fluctuations by applying threshold filters (EPS).
Only significant changes trigger new serial output, reducing spam.

#### Key Outcome: The PLC continuously monitors sensor values sent from the Raspberry Pi and can later use them to drive actuators or alarms.<br><br>
### 2. Raspberry Pi (Sensor + Blockchain – sensor_blockchain.py)

The Python script demonstrates the data acquisition and blockchain anchoring pipeline:

- Sensor Interface

- Reads analog signals from an MQ gas sensor using an ADS1115 ADC via I²C.

- Performs calibration in clean air to determine baseline R0.

- Computes Rs and the ratio Rs/R0.

- Emission Data XML

Formats sensor readings into an XML payload:
```xml
<EmissionData>
  <DeviceID>MQ_01</DeviceID>
  <Timestamp>2025-08-17T10:00:00Z</Timestamp>
  <GasType>CO2</GasType>
  <Voltage unit="V">0.542</Voltage>
  <SensorResistance unit="ohm">9,800</SensorResistance>
  <RsOverR0>1.235</RsOverR0>
  <Location>Warehouse_A</Location>
</EmissionData>
```

#### Saves the payload as a timestamped .xml file in ~/dpp_samples/.

### Blockchain Integration

Hashes the XML payload using SHA-256.

Anchors the hash to an Ethereum in-memory blockchain (EthereumTester).

Stores the proof of immutability on-chain, along with transaction details (TX hash, block number).

#### Key Outcome: The Pi acts as both a sensor gateway and a blockchain anchor node, bridging the physical and digital layers.<br><br>
<img width="800" height="900" alt="Untitled diagram _ Mermaid Chart-2025-08-17-123228" src="https://github.com/user-attachments/assets/6ecd6a90-d66c-4e83-8388-8375bb430b63" />


### 3. PLC Codes (.plcproj)

A separate PLC-IDE/ folder will later include IEC 61131-3 compliant PLC projects (.plcproj) created with the Arduino PLC IDE, showcasing ladder logic or structured text versions of the same workflow.

# 🔗 End-to-End Flow

1. Raspberry Pi reads CO₂ sensor → converts values → builds XML.

2. Raspberry Pi anchors XML hash on blockchain → proof of immutability.

3. Arduino Opta PLC connects to Pi via Modbus TCP → polls sensor values in real time.

4. PLC can use these values for decision-making (e.g., trigger ventilation, alarms, or actuators).

5. This creates a verifiable chain of trust:

#### Physical Layer (sensor) → Digital Layer (XML + blockchain) → Control Layer (PLC).

# 🚀 Getting Started
### Hardware Requirements

- Arduino Opta PLC (Ethernet-capable PLC)

- Raspberry Pi (any model with I²C + Ethernet)

- ADS1115 ADC module

- MQ-series gas sensor (e.g., MQ-135 for CO₂ equivalent)

- Ethernet network (or direct cable Pi ↔ Opta)

### Software Requirements

- Arduino IDE with ArduinoModbus and Ethernet libraries

- Python 3 with dependencies:

`pip install adafruit-circuitpython-ads1x15 web3`

- Local EthereumTester (built into Web3.py)

# 🎯 Use Cases

**Supply Chain Sustainability:** Tamper-proof CO₂ emission logs tied to Digital Product Passports.

**IoT–PLC Interoperability:** Real-time monitoring where industrial controllers can act on IoT sensor data.

**Research Prototypes:** Academic demonstration of blockchain-based sustainability tracking.<br><br>
<img width="3840" height="4000" alt="Untitled diagram _ Mermaid Chart-2025-08-17-123155" src="https://github.com/user-attachments/assets/ad7b3dd9-9ac4-452b-8fd6-3e22e7866f53" />


# 📜 License

This project is licensed under the MIT License – see the LICENSE file for details.
