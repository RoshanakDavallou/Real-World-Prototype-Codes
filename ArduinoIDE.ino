#include <SPI.h>
#include <Ethernet.h>
#include <ArduinoModbus.h>

// ---------- Network config ----------
byte MAC[] = { 0x02, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5 };
IPAddress optaIP(192,168,60,2);   // OPTA = .2
IPAddress piIP (192,168,60,1);    // Pi   = .1
IPAddress subnet(255,255,255,0);

EthernetClient   ethClient;
ModbusTCPClient  modbusClient(ethClient);

// last printed values (init to impossible)
float lastV = -1.0f;
float lastRsK = -1.0f;
float lastRatio = -1.0f;

// thresholds to avoid spamming small fluctuations
const float EPS_VOLT  = 0.001f;   // 1 mV
const float EPS_RSK   = 0.1f;     // 0.1 kΩ
const float EPS_RATIO = 0.001f;   // 0.001 on Rs/R0

unsigned long lastPoll = 0;
const unsigned long POLL_MS = 1000;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Ethernet.begin(MAC, optaIP, piIP, piIP, subnet);
  Serial.print("Static OPTA IP: ");
  Serial.println(Ethernet.localIP());

  if (!modbusClient.begin(piIP, 502)) {
    Serial.println("Modbus connect failed!");
    while (1);
  }
  Serial.println("Connected to Raspberry Pi Modbus server");
}

void loop() {
  if (millis() - lastPoll < POLL_MS) return;
  lastPoll = millis();

  if (!modbusClient.connected()) {
    modbusClient.begin(piIP, 502);
  }

  // Read 3 holding registers HR0..HR2 (addr 0..2), UnitID=1
  if (modbusClient.requestFrom(1, HOLDING_REGISTERS, 0, 3)) {
    int hr0_mv    = modbusClient.read(); // mV
    int hr1_kohm  = modbusClient.read(); // kΩ
    int hr2_ratio = modbusClient.read(); // (Rs/R0)*1000

    float voltage    = hr0_mv / 1000.0f;
    float rs_kohm    = (float)hr1_kohm;
    float rs_over_r0 = hr2_ratio / 1000.0f;

    bool changed =
      (fabs(voltage - lastV)   > EPS_VOLT)  ||
      (fabs(rs_kohm - lastRsK) > EPS_RSK)   ||
      (fabs(rs_over_r0 - lastRatio) > EPS_RATIO);

    if (changed || lastV < 0) {
      Serial.print("Voltage: ");
      Serial.print(voltage, 3);
      Serial.print(" V | Rs: ");
      Serial.print(rs_kohm, 1);
      Serial.print(" kΩ | Rs/R0: ");
      Serial.println(rs_over_r0, 3);

      lastV = voltage;
      lastRsK = rs_kohm;
      lastRatio = rs_over_r0;
    }
  } else {
    Serial.print("Modbus read failed, err=");
    Serial.println(modbusClient.lastError());
  }
}
