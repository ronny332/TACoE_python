import logging
from CoE_Types import CoE_Types as CoE_Types


class CoE_Frame(object):
    """
    stores and handles CoE raw data, received from an UDP call
    """

    rawdataLength = 14
    types = CoE_Types.getInstance()

    def __init__(self, payload):
        super().__init__()

        if not isinstance(payload, bytes) or len(payload) != self.rawdataLength:
            raise TypeError('invalid type or wrong length of raw data.')

        logging.debug('new raw CoE frame: {}'.format(str(payload)))
        self.payload = payload

        logging.debug('Frame initialized')

    def __str__(self):
        """string representation of payload

        Returns:
            string: string representation
        """
        return ''.join(['%(num)2x/%(num)-3d ' % {'num': int(p)} for p in self.payload])

    def getNode(self):
        """first byte of self.payload is node number

        Returns:
            int: node number
        """

        print()

        return int(self.payload[0])

    def getValue(self, index, type):
        pass
