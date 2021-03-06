import asyncio
import datetime
import logging
import sys
from time import time

from config import config as config

#  Data Frame Scheme:
#  analogue: [Node Number|1 byte|0-FF] [Frame Number|1 byte|1-8] [val1-4|2 bytes each|LE16] [unit val1-4|1 byte each|0-FF]
#  digital:  [Node Number|1 byte|0-FF] [Map Number|1 byte|0x0 or 0x9] [val1-16|2 bytes|binary]
class Frame(object):
    """
    stores and handles CoE raw data, received from an UDP call
    """

    highMapping = 0b1001  # 0x09, at least "frame" 9
    modified = False
    rawData = None
    rawdataLength = 14
    timestamp = None

    def __init__(self, rawData=False):  # sourcery skip: remove-redundant-if
        super().__init__()

        if rawData != False and (not isinstance(rawData, bytes) or len(rawData) != self.rawdataLength):
            raise TypeError("invalid type or wrong length of raw data.")

        self.timestamp = time()

        if rawData:
            self.rawData = rawData

            if config["frame"]["debug"]:
                logging.debug(f'Frame {self.getString(verbose=config["debug"]["verbose"])}')
            if config["frame"]["bell"]:
                asyncio.run(self.bell())
        else:
            self.rawData = bytearray(self.rawdataLength)

            if config["frame"]["debug"]:
                logging.debug(f"Frame with {self.rawdataLength} empty bytes created.")
                logging.debug(f'Frame {self.getString(verbose=config["debug"]["verbose"])}')

    def __str__(self):
        """string representation of rawData

        Returns:
            string: string representation
        """
        return self.getString(verbose=False)

    async def bell(self):
        """writes a bell symbol to the shell prompt, if shell is enabled as module."""
        sys.stdout.write("\r🔔> ")
        await asyncio.sleep(1 / 4)
        sys.stdout.write("\r  > ")

    def get16BitIntFromAnalogueValue(self, value, decimals):
        """creates an TACoE compatible integer value for given value and decimals.

        Raises:
            ValueError: calculated value needs to be between 0 and 65535

        Returns:
            integer: 0-65535 (16bit)
        """
        if (
            (not isinstance(value, int) and not isinstance(value, float))
            or not isinstance(decimals, int)
            or decimals not in range(3)
            or int(value * pow(10, decimals)) not in range(65536)
        ):
            raise ValueError("calculated value needs to be between 0 and 65535")

        return int(value * pow(10, decimals))

    def getAnalogue(self, index):
        """generate (raw) analogue values from 2 8 bit represenations at index (1-4), read as 16LE
        no precision or conversation in done, do this with the matching type details

        Args:
            index (int): values from 1 to 4

        Returns:
            tuple: (node number as integer, index number as integer, 16bit LittleEndian representation of value at index, type as integer, timestamp of creation)
        """
        if index not in range(1, 5):
            raise ValueError("only indexes between 1 and 4 are valid")

        return (
            self.getNode(),
            self.getIndex(index, True),
            self.rawData[index * 2 + 1] << 8 | self.rawData[index * 2],
            self.rawData[9 + index],
            self.timestamp,
        )

    def getData(self):
        """bytes version of self.rawData

        Returns:
            bytes: data representation
        """
        return bytes(self.rawData)

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
        num = self.rawData[3] << 8 | self.rawData[2]

        return (self.getNode(), index, num & indexAsBits == indexAsBits, self.timestamp)

    def getFrame(self):
        """second byte of self.rawData is frame number, don't use on digital frame data.
        For digital frames this method returns 0 for "low" and 9 for "high"

        Returns:
            int: frame number
        """

        return int(self.rawData[1])

    def getIndex(self, index, analogue=True):
        """get the value number (position) as integer (1-32)

        Args:
            index (int): index in frame (1-4 for analoge values, 1-32 for digital)

        Returns:
            int: value from 1 to 16
        """
        if index not in range(1, 33):
            raise ValueError("index has to be within range of 1 to 32")

        if analogue:
            return (self.getFrame() - 1) * 4 + index

        if index > 16:
            index -= 16
        if self.isMapped():
            index += 16
        return index

    def getNode(self):
        """first byte of self.rawData is node number

        Returns:
            int: node number
        """

        return int(self.rawData[0])

    def getString(self, verbose=False):
        """create string representation of self.rawData

        Returns:
            string: from self.rawData
        """
        if self.isEmpty():
            return ""

        if verbose:
            return f"{datetime.datetime.fromtimestamp(self.timestamp)} " + "".join(
                map(
                    lambda p, i: "[b%(i)d:%(p)02xh|%(p)03dd] " % {"i": i, "p": int(p)},
                    self.rawData,
                    range(self.rawdataLength),
                )
            )
        else:
            return "".join(
                map(
                    lambda p, i: "[%(p)02xh]" % {"p": int(p)},
                    self.rawData,
                    range(self.rawdataLength),
                )
            )

    def getTimestamp(self):
        """return integer representation of timestamp

        Returns:
            int: timestamp
        """
        return int(self.timestamp)

    def getTupleForIndex(self, index, analogue=False, digital=False):
        """creates a tuple for (index, frame) from external index value and anlogue/digital decision.

        Args:
            index (integer): index value
            analogue (bool, optional): index is of analogue type. Defaults to False.
            digital (bool, optional): index is of digital type. Defaults to False.

        Raises:
            ValueError: wrong value for index.

        Returns:
            tuple: (index, frame)
        """
        if analogue:
            if index not in range(1, 17):
                raise ValueError("analogue index has to be between 1 and 16")
            return (int((index - 1) % 4) + 1, int((index - 1) / 4) + 1)
        elif digital:
            if index not in range(1, 33):
                raise ValueError("digital index has to be between 1 and 32")
            return (int((index - 1) % 16) + 1, 0 if int(index) < 17 else 9)
        else:
            return False

    def isAnalogue(self):
        """detects if frame is has analogue data.
        analogue frames have a number of 1,2,3 or 4.

        Returns:
            bool: data is analogue or not
        """
        return self.rawData[1] in range(1, 9)

    def isDigital(self):
        """the opposite of isAnaloge
        digital frames have a number of 0 or 9.

        Returns:
            bool: data is digital or not
        """
        return not self.isAnalogue()

    def isEmpty(self):
        """checks if the rawData has any non zero entries

        Returns:
            bool: is empty or not
        """

        return not self.rawData or not isinstance(self.rawData, (bytearray, bytes)) or not any(self.rawData)

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
        return self.rawData[1] == self.highMapping

    def isModified(self):
        """currently just simple wrapper for self.modified

        Returns:
            boolean: is modified
        """
        return self.modified

    def isMutable(self):
        """only bytearrays are muteable, bytes instances aren't

        Returns:
            bool: rawData/frame data can be modified
        """
        return isinstance(self.rawData, bytearray)

    def setAnalogue(self, frame, index, value):
        """sets the analogue value. value has to be already been recalculated to plain integer value.

        Args:
            frame (int): frame number
            index (int): index number
            value (int): value as integer

        Raises:
            ValueError: invalid input.
            ValueError: Frame number already set, can't use a different one with the same frame.
        """
        if index not in range(1, 5) and frame not in range(1, 9) and value not in range(65536):
            raise ValueError("invalid input.")

        if self.isModified() and frame != self.getFrame():
            raise ValueError("Frame number already set, can't use a different one with the same frame.")
        elif not self.isModified():
            self.setFrame(frame)
        self.setValueAtIndex(index, value)

    def setDigital(self, frame, index, value):
        """sets the digital value. value has to be already been recalculated to plain integer value [0, 1].

        Args:
            frame (int): frame number
            index (int): index number
            value (int): value as integer ([0, 1])

        Raises:
            ValueError: invalid input.
            ValueError: Frame number already set, can't use a different one with the same frame.
        """
        if index not in range(1, 17) and frame not in [0, 9] and value not in [0, 1]:
            raise ValueError("invalid input.")

        if self.isModified() and frame != self.getFrame():
            raise ValueError("Frame number already set, can't use a different one with the same frame.")
        elif not self.isModified():
            self.setFrame(frame)
        self.setValueAtBit(index, value)

    def setFrame(self, frame):
        """Set the frame to value between 0 and 9
        0 and 9 means digital frame (0 = low mapping, 9 = high mapping)
        1-8 means analogue

        Args:
            frame (integer: frame number

        Raises:
            ValueError: frame number has to be between 0 and 9.
            TypeError: Frame not mutable.
        """
        if frame not in range(10):
            raise ValueError("frame number has to be between 0 and 9.")
        if not self.isMutable():
            raise TypeError("Frame not mutable.")

        if not self.isModified():
            self.setModified()
        else:
            if frame != self.getFrame():
                raise ValueError("Frame already set and not equal with new one.")
        self.rawData[1] = frame

    def setModified(self):
        """set self.modified to true"""
        self.modified = True

    def setNode(self, node):
        """Sets the node number of current frame (0-255).

        Args:
            node ([type]): [description]

        Raises:
            ValueError: [description]
            TypeError: [description]
        """
        if node not in range(256):
            raise ValueError("node number has to be between 0 and 255.")
        if self.getNode() not in [0, node]:
            raise ValueError("Node value already set, create a new frame with another value.")
        if not self.isMutable():
            raise TypeError("Frame not mutable.")

        self.rawData[0] = node

    def setTimestamp(self):
        """timestamp to property"""
        self.timestamp = self.getTimestamp()

    def setUnit(self, index, unit=1):
        """TODO

        Args:
            index ([type]): [description]
            type (int, optional): [description]. Defaults to 1.

        Raises:
            ValueError: [description]
            TypeError: [description]
        """
        if index not in range(1, 5):
            raise ValueError("Index has to be between 1 and 4.")
        if not self.isAnalogue():
            raise TypeError("Only analogue type has units.")

        self.rawData[9 + index] = unit

    def setValue(self, node, index, value, decimals=0, analogue=False, digital=False):
        """set analogue or digital values at node/index/frame. Frame gets calculated
        automatically from index value.

        Args:
            node (int): node number
            index (int): index number
            value (str/int/float): value to stored, is internally stored as plain integer.
            decimals (int, optional): decimals of analogue values Defaults to 0.
            analogue (bool, optional): value is analogue. Defaults to False.
            digital (bool, optional): value is digital. Defaults to False.

        Raises:
            ValueError: node has to be between 0 and 255.
            ValueError: index has to be between 1 and 16 for analogue frames.
            ValueError: value has to be integer value between 0 and 65535.
            ValueError: decimals have to be between 0 and 2.
            ValueError: index has to be between 1 and 32 for digital frames.
            ValueError: value has to be a boolean value for digital values.
            ValueError: either analogue or digital have to be true.
        """
        if node not in range(256):
            raise ValueError("node has to be between 0 and 255.")
        if analogue:  # analogue
            type = "analogue"
            if isinstance(value, str):
                value = float(value)
            if index not in range(1, 17):
                raise ValueError("index has to be between 1 and 16 for analogue frames.")
            if int(value) not in range(pow(2, 16)):
                raise ValueError("value has to be integer value between 0 and 65535.")
            if decimals not in range(3):
                raise ValueError("decimals have to be between 0 and 2.")
        elif digital:  # digital
            type = "digital"

            if index not in range(1, 33):
                raise ValueError("index has to be between 1 and 32 for digital frames.")
            if value not in range(2) and value not in [True, False]:
                raise ValueError("value has to be a boolean value for digital values.")
        else:
            raise ValueError("either analogue or digital have to be true.")

        self.setNode(node)

        if type == "analogue":
            rawValue = self.get16BitIntFromAnalogueValue(value, decimals)
            (rawIndex, rawFrame) = self.getTupleForIndex(index, analogue=True)

            self.setAnalogue(rawFrame, rawIndex, rawValue)
        else:
            rawValue = 1 if value else 0
            (rawIndex, rawFrame) = self.getTupleForIndex(index, digital=True)

            self.setDigital(rawFrame, rawIndex, rawValue)

    def setValueAtBit(self, index, value):
        """bitwise setter for binary values

        Args:
            index (index): index of frame
            value (int): [0, 1] binary value

        Raises:
            ValueError: Index has to be between 1 and 16, for values 17 to 32 use high mapping.
        """
        if index not in range(1, 17):
            raise ValueError("Index has to be between 1 and 16, for values 17 to 32 use high mapping.")
        indexAsBits = 1 << ((index - 1) % 16)

        highByte = indexAsBits >> 8 & 0xFF
        lowByte = 0xFF & indexAsBits

        if value == 1:
            self.rawData[2] |= lowByte
            self.rawData[3] |= highByte
        else:
            self.rawData[2] ^= lowByte
            self.rawData[3] ^= highByte

        # TODO

    def setValueAtIndex(self, index, value):
        """TODO only for analogue values

        Args:
            index ([type]): [description]
            value ([type]): [description]

        Raises:
            TypeError: [description]
            TypeError: [description]
            ValueError: [description]
            ValueError: [description]
        """
        if not self.isAnalogue():
            raise TypeError("Frame is not of type analogue.")
        if not self.isMutable():
            raise TypeError("Frame not mutable.")
        if index not in range(1, 5):
            raise ValueError("Index has to be between 1 and 4.")
        if value not in range(65536):
            raise ValueError("Value has to be between 0 and 65535.")

        self.rawData[index * 2] = (value & 0xFF).to_bytes(1, byteorder="little")[0]
        self.rawData[index * 2 + 1] = (value >> 8 & 0xFF).to_bytes(1, byteorder="little")[0]
        self.setUnit(index, unit=1)  # just 1 for °C for now, rest TODO
