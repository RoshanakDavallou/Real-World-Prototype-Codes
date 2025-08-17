import os, time, hashlib, pathlib
from datetime import datetime, timezone

# ---- Sensor / ADC
import board, busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ---- Blockchain (local test chain in memory)
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider

# ------------------ Config ------------------
VCC = 3.3          # Sensor supply (3.3V on Raspberry Pi)
RL  = 10000.0      # Load the resistor on MQ module (Ω) – typical 10k
DEVICE_ID = "MQ_01"
LOCATION  = "Warehouse_A"
GAS_TYPE  = "CO2"  # adjust label for your paper

SAVE_DIR = pathlib.Path.home() / "dpp_samples"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
# --------------------------------------------

# I2C / ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P1)

def read_voltage_avg(n=10, delay=0.1):
    vals = []
    for _ in range(n):
        vals.append(chan.voltage)
        time.sleep(delay)
    return sum(vals)/len(vals)

def rs_from_vout(vout):
    # Rs = RL * (Vcc - Vout) / Vout
    # Guard against divide-by-zero
    v = max(vout, 1e-6)
    return RL * (VCC - v) / v

print("\n=== Calibration (clean air) for R0 (about 5 seconds) ===")
cal_volt = read_voltage_avg(n=25, delay=0.2)
R0 = rs_from_vout(cal_volt)
print(f"Cal Vout: {cal_volt:.3f} V | R0: {R0:,.1f} Ω\n")

print("=== Taking a measurement sample ===")
vout = read_voltage_avg(n=10, delay=0.1)
Rs = rs_from_vout(vout)
ratio = Rs / R0
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print(f"Timestamp: {now}")
print(f"DeviceID : {DEVICE_ID}")
print(f"Vout     : {vout:.3f} V")
print(f"Rs       : {Rs:,.1f} Ω")
print(f"Rs/R0    : {ratio:.3f}")
print(f"GasType  : {GAS_TYPE}")
print(f"Location : {LOCATION}")

# If the sensor is MQ-135 and we want a rough CO2 estimate, we can uncomment:
# import math
# ppm = 116.6 * (ratio ** -2.77)
# print(f"Approx CO2: {ppm:.1f} ppm")

# --- Build XML ---
xml = f"""<EmissionData>
  <DeviceID>{DEVICE_ID}</DeviceID>
  <Timestamp>{now}</Timestamp>
  <GasType>{GAS_TYPE}</GasType>
  <Voltage unit="V">{vout:.3f}</Voltage>
  <SensorResistance unit="ohm">{Rs:.1f}</SensorResistance>
  <RsOverR0>{ratio:.3f}</RsOverR0>
  <Location>{LOCATION}</Location>
</EmissionData>
""".strip()

fname = SAVE_DIR / f"emission_{now.replace(':','').replace('-','')}.xml"
with open(fname, "w", encoding="utf-8") as f:
    f.write(xml)

print("\n=== XML Payload (also saved to file) ===")
print(xml)
print(f"\nSaved XML → {fname}")

# --- Hash XML (immutability proof) ---
h = hashlib.sha256(xml.encode("utf-8")).hexdigest()
print(f"\nSHA-256(XML): {h}")

# --- Send hash to a local in-memory blockchain (EthereumTester) ---
w3 = Web3(EthereumTesterProvider())
acct = w3.eth.accounts[0]            # pre-funded test account
tx = {
    "from": acct,
    "to": acct,                      # self-transfer with data (demo)
    "value": 0,
    "data": bytes.fromhex(h),        # put the hash in the data field
}

tx_hash = w3.eth.send_transaction(tx)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"\nBlockchain TX Hash: {tx_hash.hex()}")
print(f"Block Number      : {receipt.blockNumber}")
