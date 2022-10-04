import time

from ctypes import c_short


class Utils:
    """A class providing necessary functions to interact with BME280

    After instantiating a Utils object, initializeSettings() has to be called to enable
    measurements
    """

    def __init__(self, address, bus):
        """Initializes object default values, and sets device address

        Args:
            address (int): Hardware address of the device
            bus (int): specifies the i2c bus
        """

        self.address = address
        self.bus = bus
        self.initialized = False
        self.dig_T1, self.dig_T2, self.dig_T3, self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4 = 0, 0, 0, 0, 0, 0, 0
        self.dig_P5, self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9, self.dig_H1, self.dig_H2 = 0, 0, 0, 0, 0, 0, 0
        self.dig_H3, self.dig_H4, self.dig_H5, self.dig_H6 = 0, 0, 0, 0
        self.op = 0
        self.ot = 0
        self.oh = 0
        self.mode = 0

    def readChipId(self):
        """Reads ChipID

        Returns:
            Chip-ID of the connected BME280
        """

        ID = 0xD0
        (chip_id, chip_version) = self.bus.read_i2c_block_data(self.address, ID, 2)
        return chip_id, chip_version

    def softReset(self):
        """Resets all settings on device (documentation 5.4.2)"""
        RESET = 0xE0
        self.bus.write_byte_data(self.address, RESET, 0xB6)
        time.sleep(2 / 1000)

    def initializeSettings(self, mode, ot, oh, op):
        """writes settings to device (see doc 5.4.5)

        Args:
            mode (int): specifies measurement mode
            ot (int): specifies oversampling of temperature
            oh (int): specifies oversampling of humidity
            op (int): specifies oversampling of pressure

        """
        self.ot = ot
        self.op = op
        self.oh = oh
        self.mode = mode

        CTRL_HUM = 0xF2
        CTRL_MEAS = 0xF4
        compoundSettings = ot << 5 | op << 2 | mode

        self.bus.write_byte_data(self.address, CTRL_HUM, oh)
        self.bus.write_byte_data(self.address, CTRL_MEAS, compoundSettings)

        self._computeCompData()
        self.initialized = True
        time.sleep(4 / 1000)

    # relevant in forced mode, because mode is reset to sleep once forced measurement is complete
    # see documentation 3.3.1
    def _refreshSettings(self):
        """Rewrites settings to device, to trigger measurement in forced mode (see doc 3.3.3)"""
        compoundSettings = self.ot << 5 | self.op << 2 | self.mode
        CTRL_MEAS = 0xF4
        self.bus.write_byte_data(self.address, CTRL_MEAS, compoundSettings)

    def _readCompData(self):
        """Reads registers containing trimming parameters from device (see doc 4.2.2)

        Returns:
            trimming parameters read from device as two values
        """
        CALIB00 = 0x88
        CALIB26 = 0xE1

        calib1 = self.bus.read_i2c_block_data(self.address, CALIB00, 25)
        calib2 = self.bus.read_i2c_block_data(self.address, CALIB26, 7)

        return calib1, calib2

    def _computeCompData(self):
        """Splits trimming parameter register into individual trimming values,
         saves as object variables (see doc 4.2.2)"""

        calib1, calib2 = self._readCompData()

        self.dig_T1 = self._getUShort(calib1, 0)
        self.dig_T2 = self._getShort(calib1, 2)
        self.dig_T3 = self._getShort(calib1, 4)
        self.dig_P1 = self._getUShort(calib1, 6)
        self.dig_P2 = self._getShort(calib1, 8)
        self.dig_P3 = self._getShort(calib1, 10)
        self.dig_P4 = self._getShort(calib1, 12)
        self.dig_P5 = self._getShort(calib1, 14)
        self.dig_P6 = self._getShort(calib1, 16)
        self.dig_P7 = self._getShort(calib1, 18)
        self.dig_P8 = self._getShort(calib1, 20)
        self.dig_P9 = self._getShort(calib1, 22)
        self.dig_H1 = self._getUChar(calib1, 24)

        self.dig_H2 = self._getShort(calib2, 0)
        self.dig_H3 = self._getUChar(calib2, 2)
        self.dig_H4 = (self._getChar(calib2, 3) << 4) | ((self._getChar(calib2, 4)) & 0x0F)
        self.dig_H5 = (self._getChar(calib2, 5) << 4) | ((self._getUChar(calib2, 4)) >> 4 & 0x0F)
        self.dig_H6 = self._getChar(calib2, 6)

    @staticmethod
    def _getUShort(item, index):
        return (item[index + 1] << 8) | item[index]

    @staticmethod
    def _getShort(item, index):
        return c_short((item[index + 1] << 8) | item[index]).value

    @staticmethod
    def _getChar(item, index):
        if item[index] > 127:
            return item[index] - 256
        return item[index]

    @staticmethod
    def _getUChar(item, index):
        return 0xFF & item[index]

    # documentation offers several compensation formulas, the one below has the highest accuracy
    def readTHP(self):
        """Triggers measurement and returns compensated measured values (see doc 8.2)

        Returns:
            temperature in degree Celsius
            humidity in percent
            pressure in hPa
        """

        if not self.initialized:
            return

        values = self.readTHPRaw()
        ut = values[0]
        uh = values[1]
        up = values[2]

        # compensate temperature
        var1 = ((ut / 16384) - (self.dig_T1 / 1024)) * self.dig_T2
        var2 = (((ut / 131072.0) - (self.dig_T1 / 8192.0)) * ((ut / 131072.0) - (self.dig_T1 / 8192.0))) * self.dig_T3
        temperature = (var1 + var2) / 5120

        # compensate pressure
        var1 = temperature / 2 - 64000
        var2 = var1 * var1 * self.dig_P6 / 32768
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = (var2 / 4.0) + (self.dig_P4 * 65536.0)
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            return 0
        p = 1048576.0 - up
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = self.dig_P9 * p * p / 2147483648.0
        var2 = p * self.dig_P8 / 32768.0
        pressure = p + (var1 + var2 + self.dig_P7) / 16.0

        # compensate humidity
        var_H = (temperature - 76800.0)
        var_H = (uh - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * var_H)) * (self.dig_H2 / 65536.0 * (
                1.0 + self.dig_H6 / 67108864.0 * var_H * (1.0 + self.dig_H3 / 67108864.0 * var_H)))
        var_H = var_H * (1.0 - self.dig_H1 * var_H / 524288.0)
        if var_H > 100:
            var_H = 100
        elif var_H < 0:
            var_H = 0
        humidity = var_H

        return temperature, humidity, pressure / 100

    def readTHPRaw(self):
        """Triggers measurement and returns uncompensated measured values (see doc 4.1)
        Initially refreshes settings on device, then waits until status register indicates
        measurement done, before reading relevant registers

         Returns:
             20-bit temperature register
             16-bit humidity register
             20-bit pressure register
         """
        if not self.initialized:
            return

        self._refreshSettings()
        wait = 1 + (2 * self.ot) + (2 * self.op + 0.5) + (2 * self.oh + 0.5)
        time.sleep(wait / 1000)

        STATUS = 0xF3
        state = (self.bus.read_i2c_block_data(self.address, STATUS, 1))

        while (state[0] >> 3) % 2 != 0:
            state = (self.bus.read_i2c_block_data(self.address, STATUS, 1))
            time.sleep(wait / 1000)

        result = self.bus.read_i2c_block_data(self.address, 0xF7, 8)
        up = (result[0] << 12) | (result[1] << 4) | (result[2] >> 4)
        ut = (result[3] << 12) | (result[4] << 4) | (result[5] >> 4)
        uh = (result[6] << 8) | result[7]

        return ut, uh, up
