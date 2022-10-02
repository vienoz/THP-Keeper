import time
import smbus

from utils import Utils


def test(addr, bus):
    print("running self-test...")
    testSetup = Utils(addr, bus)

    # Communication test
    try:
        testSetup.softReset()
    except:
        return "10 Communication error or wrong device found"

    # Bond wire test
    testSetup.initialize(1, 1, 1, 1)
    testMeasurement = testSetup.readTHPRaw()
    if (testMeasurement[0] & 0xFFFFF) == 0 or (testMeasurement[0] & 0xFFFFF) == 0xFFFFF:
        return "30 Temperature bond wire failure or MEMS defect"
    if (testMeasurement[2] & 0xFFFFF) == 0 or (testMeasurement[2] & 0xFFFFF) == 0xFFFFF:
        return "31 Pressure bond wire failure or MEMS defect"

    # Measurement plausibility test
    testMeasurement = testSetup.readTHP()
    if testMeasurement[0] > 40 or testMeasurement[0] < 0:
        return "40 Implausible temperature (default limits: 0...40°C)"
    if testMeasurement[1] > 80 or testMeasurement[1] < 20:
        return "42 Implausible humidity (default limits: 20...80 %rH)"
    if testMeasurement[2] > 1100 or testMeasurement[2] < 900:
        return "41 Implausible pressure (default limits: 900...1100 hPa)"

    return 0


def main():
    if (test(0x76, smbus.SMBus(1))) == 0:
        print("Sensor OK")


if __name__ == '__main__':
    main()
