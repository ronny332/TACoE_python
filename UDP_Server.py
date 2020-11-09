from collections import deque
import logging
import socket
import threading

from CoE_Frame import CoE_Frame

from config import config

class UDP_Server(threading.Thread):
    """
    listen on port 5441 and receives 14 byte CoE UDP packets and stores them into a FIFO queue
    """

    __instance = None

    frames = deque(maxlen=config["udp_server"]["fifo_length"])
    udp_port = config["udp_server"]["udp_port"]

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

        logging.debug(f'UDP server initiated with fifo size of {self.frames.maxlen} frames, listening on UDP port {self.udp_port}')

    def getFrames(self):
        """return frames object

        Returns:
            queue: frames object
        """
        return self.frames

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
                except TypeError as type_error:
                    logging.error(type_error)
