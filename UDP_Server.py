from collections import deque
import logging
import socket
import threading

from CoE_Frame import CoE_Frame


class UDP_Server(threading.Thread):
    """
    listen on port 5441 and receives 14 byte CoE UDP packets and stores them into a FIFO queue
    """

    __instance = None

    @staticmethod
    def getInstance():
        """Static access method for UDP_Server """
        if UDP_Server.__instance is None:
            UDP_Server()
        return UDP_Server.__instance

    def __init__(self):
        super().__init__()

        if UDP_Server.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            UDP_Server.__instance = self

        self.fifo_length = 100
        self.frames = deque(maxlen=self.fifo_length)
        self.udp_port = 5441

        logging.debug('UDP server initiated')

    def run(self):
        """run the UDP_Server thread
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', self.udp_port))

            while True:
                data, _ = s.recvfrom(CoE_Frame.rawdataLength)
                try:
                    frame = CoE_Frame(data)
                    self.frames.append(frame)
                    logging.info(f'created new frame ({CoE_Frame.rawdataLength} bytes): ' +
                                 f'{self.frames[-1]}')
                except TypeError as type_error:
                    logging.error(type_error)

                print(self.frames[-1].getNode())
