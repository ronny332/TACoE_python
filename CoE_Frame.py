import logging


class CoE_Frame(object):
    """
    stores and handles CoE raw data, received from an UDP call
    """

    rawdataLength = 14

    def __init__(self, payload):
        if not isinstance(payload, bytes) or len(payload) != self.rawdataLength:
            raise TypeError('invalid type or wrong length of raw data.')

        logging.debug('got new raw CoE frame: {}'.format(str(payload)))
        self.payload = payload

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
        return int(self.payload[0])
