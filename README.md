# THP-Monitor 


## 📜 Summary
A simple implementation of some core features of the BME280 specification, that periodically measures and stores temperature, humidity and pressure. Tested on Raspberry Pi, but should run on any I2C capable device connected to a BME280.

## 📋 Requirements
* communication is done via I2C which, on the Raspberry Pi, has to be activated in Configuration under `Interface Options`
* correct GPIO connections (on Raspberry Pi):
  * ADDR-> GROUND
  * SCL/SCK -> GPIO4
  * SDA/MOSI -> GPIO2
  * GND -> GROUND
  * VCC -> 3V3

## 🛠️ Implementation
The implementation is based on the [official BME280 data sheet](https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/#documents) revision 1.23. Utils.py includes tools to interact with the BME280 which is used by selftest.py that runs a quick self check and main.py that periodically stores the measurements. Selftest.py strictly adheres to specification with quite tight parameter windows that can be adjusted, trimming parameter and chip ID validation are not implemented. Measurement intervals and measured parameters can be adjusted in main.py.

## ⚠️ Troubleshooting
* IO ERROR: use `i2cdetect -y 1` to see if BME280 is properly connected to the device, should be at address 76.
* self-test failure: depending on error code, adjust default limits or verify proper connections. For further information, see 10.1 in the specification.
