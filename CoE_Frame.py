import asyncio
import datetime
import logging
import sys
from time import time

from config import config as config
from CoE_Types import CoE_Types as CoE_Types

#
#  Data Frame Scheme:
#  [Node Number|1 byte|0-FF][Frame Number|1 byte|1-4]
#


class CoE_Frame(object):
    """
    stores and handles CoE raw data, received from an UDP call
    """

    highMapping = 0b1001  # 0x09, at least "frame" 9
    payload = None
    rawdataLength = 14
    timestamp = None
    types = CoE_Types.getInstance()

    def __init__(self, payload):
        super().__init__()

        if not isinstance(payload, bytes) or len(payload) != self.rawdataLength:
            raise TypeError('invalid type or wrong length of raw data.')

        self.payload = payload
        self.timestamp = time()

        if config["modules"]["coe_frame"]["debug"]:
            logging.debug(
                f'CoE frame {self.getString(verbose=config["debug"]["verbose"])}')
        if config["modules"]["coe_frame"]["bell"]:
            asyncio.run(self.bell())

    def __str__(self):
        """string representation of payload

        Returns:
            string: string representation
        """
        return self.getString(verbose=False)

    async def bell(self):
        sys.stdout.write("\r🔔> ")
        await asyncio.sleep(1/4)
        sys.stdout.write("\r  > ")

    def getAnalogue(self, index):
        """generate (raw) analogue values from 2 8 bit represenations at index (1-4), read as 16LE
        no precision or conversation in done, do this with the matching type details

        Args:
            index (int): values from 1 to 4

        Returns:
            tuple: (node number as integer, index number as integer, 16bit LittleEndian representation of value at index, type as integer, timestamp of creation)
        """
        if index not in range(1, 5):
            raise ValueError('only indexes between 1 and 4 are valid')

        return (self.getNode(), self.getIndex(index, True), self.payload[index * 2 + 1] << 8 | self.payload[index * 2], self.payload[9 + index], self.timestamp)

    def getDigital(self, index):
        """get digital bool value for index.
        index gets recalculated for result tuple.
        if index is in range of 1 to 16 and result index is in "high level" the index is index + 16
        if index is in range of 17 to 32 and result index is in "low level" the index is index - 16

        Args:
            index (index): index for value (1-32)

        Returns:
            tuple: (node number as integer, index number as integer, value of index as bool, timestamp of creation)
        """
        index = self.getIndex(index, False)

        indexAsBits = 1 << ((index - 1) % 16)
        num = self.payload[3] << 8 | self.payload[2]

        return (self.getNode(), index, num & indexAsBits == indexAsBits, self.timestamp)

    def getFrame(self):
        """second byte of self.payload is frame number, don't use on digital frame data.
        For digital frames this method returns 0 for "low" and 9 for "high"

        Returns:
            int: frame number
        """

        return int(self.payload[1])

    def getIndex(self, index, analogue=True):
        """get the value number (position) as integer (1-32)

        Args:
            index (int): index in frame (1-4 for analoge values, 1-32 for digital)

        Returns:
            int: value from 1 to 16
        """
        if index not in range(1, 33):
            raise ValueError('index has to be within range of 1 to 32')

        if analogue:
            return (self.getFrame() - 1) * 4 + index
        else:
            if index > 16:
                index -= 16
            if self.isMapped():
                index += 16
            return index

    def getNode(self):
        """first byte of self.payload is node number

        Returns:
            int: node number
        """

        return int(self.payload[0])

    def getString(self, verbose=False):
        """create string representation of self.payload

        Returns:
            string: from self.payload
        """

        # if self.getNode() in [51, 52]:
        #     print(self.getAnalogueValue(1))
        #     print(self.getAnalogueValue(2))
        #     print(self.getAnalogueValue(3))
        #     print(self.getAnalogueValue(4))

        # if self.getNode() in [55, 56, 57, 58, 59, 60]:
        #     print(self.getDigitalValue(1))
        #     print(self.getDigitalValue(2))
        #     print(self.getDigitalValue(3))
        #     print(self.getDigitalValue(4))
        #     print(self.getDigitalValue(5))
        #     print(self.getDigitalValue(6))
        #     print(self.getDigitalValue(7))
        #     print(self.getDigitalValue(8))
        #     print(self.getDigitalValue(9))
        #     print(self.getDigitalValue(10))
        #     print(self.getDigitalValue(11))
        #     print(self.getDigitalValue(12))
        #     print(self.getDigitalValue(13))
        #     print(self.getDigitalValue(14))
        #     print(self.getDigitalValue(15))
        #     print(self.getDigitalValue(16))
        #     print(self.getDigitalValue(17))
        #     print(self.getDigitalValue(18))
        #     print(self.getDigitalValue(19))
        #     print(self.getDigitalValue(20))
        #     print(self.getDigitalValue(21))
        #     print(self.getDigitalValue(22))
        #     print(self.getDigitalValue(23))
        #     print(self.getDigitalValue(24))
        #     print(self.getDigitalValue(25))
        #     print(self.getDigitalValue(26))
        #     print(self.getDigitalValue(27))
        #     print(self.getDigitalValue(28))
        #     print(self.getDigitalValue(29))
        #     print(self.getDigitalValue(30))
        #     print(self.getDigitalValue(31))
        #     print(self.getDigitalValue(32))

        if verbose:
            return f'{datetime.datetime.fromtimestamp(self.timestamp)} ' + ''.join(map(
                lambda p, i: '[b%(i)d:%(p)02xh|%(p)03dd] '
                % {'i': i, 'p': int(p)},
                self.payload,
                range(self.rawdataLength)
            ))
        else:
            return ''.join(map(
                lambda p, i: '[%(p)02xh]'
                % {'p': int(p)},
                self.payload,
                range(self.rawdataLength)

            ))

    def isAnalogue(self):
        """detects if frame is has analogue data.
        analogue frames have a number of 1,2,3 or 4.

        Returns:
            bool: data is analogue or not
        """
        return self.payload[1] in range(1, 5)

    def isDigital(self):
        """the opposite of isAnaloge
        digital frames have a number of 0 or 9.

        Returns:
            bool: data is digital or not
        """
        return not self.isAnalogue()

    def isMapped(self):
        """return False for first value mapping, True for second value mapping
        digital mapping 0x0/low = value 1-16, level 0x9/high = value 17-32

        Summary: TA stores digital values in only 16 bits packet space.
        To make 32 values possible, they map the values 17 to 32 by setting the
        second byte of each paket to 0x9, what means "high". Low is 0x0.

        Use this method only on digital frames.

        Returns:
            bool: False = low/1st value level, True = high/2nd value level
        """
        return self.payload[1] == self.highMapping
