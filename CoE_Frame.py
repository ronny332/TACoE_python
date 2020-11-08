import logging
from time import time

from CoE_Types import CoE_Types as CoE_Types

#
#  Data Frame Scheme:
#  [Node Number|1 byte|0-FF][Frame Number|1 byte|1-4]
#


class CoE_Frame(object):
    """
    stores and handles CoE raw data, received from an UDP call
    """

    digitalHighLevel = 0b1001  # 0x09
    rawdataLength = 14
    types = CoE_Types.getInstance()

    def __init__(self, payload):
        super().__init__()

        if not isinstance(payload, bytes) or len(payload) != self.rawdataLength:
            raise TypeError('invalid type or wrong length of raw data.')

        self.payload = payload
        self.timestamp = time()

        logging.debug(f'CoE frame {self.getString()}')

    def __str__(self):
        """string representation of payload

        Returns:
            string: string representation
        """
        return self.getString()

    def getAnalogueValue(self, index):
        """generate (raw) analogue values from 2 8 bit represenations at index (1-4), read as 16LE
        no precision or conversation in done, do this with the matching type details

        Args:
            index (int): values from 1 to 4

        Raises:
            ValueError: index needs values between 1 and 4

        Returns:
            tuple: (node number as integer, value number as integer, 16bit LittleEndian representation of value at index, type as integer, timestamp of creation)
        """
        if index not in range(1, 5):
            raise ValueError('only indexes between 1 and 4 are valid')

        return (self.getNode(), self.getValueNumber(index), self.payload[index * 2 + 1] << 8 | self.payload[index * 2], self.payload[9 + index], self.timestamp)

    def getDigitalValue(self, index):
        if index not in range(1, 33):
            raise ValueError('index has to be within range of 1 to 32')
        if index > 16:
            index -= 16

        indexAsBits = 1 << index - 1
        num = self.payload[3] << 8 | self.payload[2]

        if self.isDigitalHighLevel():
            index += 16

        return (self.getNode(), index, num & indexAsBits == indexAsBits, self.timestamp)

    def getFrame(self):
        """second byte of self.payload is frame number, don't use on digital frame data

        Returns:
            int: frame number
        """

        return int(self.payload[1])

    def getNode(self):
        """first byte of self.payload is node number

        Returns:
            int: node number
        """

        return int(self.payload[0])

    def getString(self):
        """create string representation of self.payload

        Returns:
            string: from self.payload
        """

        # if self.getNode() in [51, 52]:
        #     print(self.getAnalogueValue(1))
        #     print(self.getAnalogueValue(2))
        #     print(self.getAnalogueValue(3))
        #     print(self.getAnalogueValue(4))

        if self.getNode() in [55, 56, 57, 58, 59, 60]:
            print(self.getDigitalValue(1))
            print(self.getDigitalValue(2))
            print(self.getDigitalValue(3))
            print(self.getDigitalValue(4))
            print(self.getDigitalValue(5))
            print(self.getDigitalValue(6))
            print(self.getDigitalValue(7))
            print(self.getDigitalValue(8))
            print(self.getDigitalValue(9))
            print(self.getDigitalValue(10))
            print(self.getDigitalValue(11))
            print(self.getDigitalValue(12))
            print(self.getDigitalValue(13))
            print(self.getDigitalValue(14))
            print(self.getDigitalValue(15))
            print(self.getDigitalValue(16))
            print(self.getDigitalValue(17))
            print(self.getDigitalValue(18))
            print(self.getDigitalValue(19))
            print(self.getDigitalValue(20))
            print(self.getDigitalValue(21))
            print(self.getDigitalValue(22))
            print(self.getDigitalValue(23))
            print(self.getDigitalValue(24))
            print(self.getDigitalValue(25))
            print(self.getDigitalValue(26))
            print(self.getDigitalValue(27))
            print(self.getDigitalValue(28))
            print(self.getDigitalValue(29))
            print(self.getDigitalValue(30))
            print(self.getDigitalValue(31))
            print(self.getDigitalValue(32))

        return ''.join(map(
            lambda p, i: '[b%(i)d:%(p)02xh|%(p)03dd] '
            % {'i': i, 'p': int(p)},
            self.payload,
            range(self.rawdataLength)
        ))

    def getValueNumber(self, index):
        """get the value number (position) as integer (1-16)

        Args:
            index (int): index in frame (1-4)

        Returns:
            int: value from 1 to 16
        """
        return self.getFrame() * 4 + index

    def isDigitalHighLevel(self):
        """return False for first value level, True for second value level
        digital level low = value 1-16, lovel high = value 17-32

        Returns:
            boolean: False = low/1st value level, True = high/2nd value level
        """
        return self.payload[1] == self.digitalHighLevel
