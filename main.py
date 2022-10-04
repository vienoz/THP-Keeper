import csv
import smbus
import selftest
import time
from utils import Utils

PORT = 1
ADDRESS = 0x76
BUS = smbus.SMBus(PORT)


def main():
    if selftest.test(ADDRESS, BUS) == 0:
        print("self-test success")

    util = Utils(ADDRESS, BUS)
    util.initializeSettings(1, 1, 1, 1)

    while True:
        temp, hum, pres = util.readTHP()
        now = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        with open('measurementLog.csv', 'a') as log:
            logWriter = csv.writer(log)
            logWriter.writerow([temp, hum, pres, now])
        print('successful measurement at', now)
        time.sleep(300)


if __name__ == '__main__':
    main()
