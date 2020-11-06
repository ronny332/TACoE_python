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

        self.payload = payload

        logging.debug(f'CoE frame {self.str()}')

    def __str__(self):
        """string representation of payload

        Returns:
            string: string representation
        """
        return self.str()

    def getNode(self):
        """first byte of self.payload is node number

        Returns:
            int: node number
        """

        return int(self.payload[0])

    def str(self):
        return ''.join(map(
            lambda p, i: '[b%(i)d:%(p)02xh/%(p)03dd]'
            % {'i': i, 'p': int(p)},
            self.payload,
            range(self.rawdataLength)
        ))

    def getValue(self, index, type):
        pass
