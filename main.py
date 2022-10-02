from smbus
import selftest
from utils import Utils

PORT = 1
ADDRESS = 0x76
bus = smbus.SMBus(PORT)

if __name__ == '__main__':

    util = Utils(ADDRESS, BUS)
    util.initialize(1, 1, 1, 1)

    print("success")

