from smbus import smbus2
import selftest
from utils import Utils

PORT = 1
ADDRESS = 0x76
BUS = smbus.SMBus(PORT)


def main():

    if selftest.test(ADDRESS, BUS) == 0:
        print("self-test success")

    util = Utils(ADDRESS, BUS)
    util.initialize(1, 1, 1, 1)

    print(util.readTHP())


if __name__ == '__main__':
    main()
