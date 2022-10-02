import time
import smbus

from utils import Utils


def test(addr, bus):
    testSetup = Utils(addr, bus)

    # Communication test
    try:
        testSetup.softReset()
    except:
        return "10 Communication error or wrong device found"

    # Bond wire test
    testSetup.initialize(1, 1, 1, 1)
    testMeasurement = testSetup.readTHP()
    if (testMeasurement[0] & 0xFFFFF) == 0 or (testMeasurement[0] & 0xFFFFF) == 0xFFFFF:
        return "30 Temperature bond wire failure or MEMS defect"
    if (testMeasurement[2] & 0xFFFFF) == 0 or (testMeasurement[2] & 0xFFFFF) == 0xFFFFF:
        return "31 Pressure bond wire failure or MEMS defect"

    # Measurement plausibility test
    if testMeasurement[0] > 40 or testMeasurement[0] < 0:
        return "40 Implausible temperature (default limits: 0...40°C)"
    if testMeasurement[0] > 40 or testMeasurement[0] < 0:
        return "41 Implausible pressure (default limits: 900...1100 hPa)"
    if testMeasurement[0] > 40 or testMeasurement[0] < 0:
        return "42 Implausible humidity (default limits: 20...80 %rH)"

    return 0


if __name__ == '__main__':
    print(test(0x76, smbus.SMBus(1)))
