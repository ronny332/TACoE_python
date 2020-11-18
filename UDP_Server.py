from collections import deque
import logging
import socket
import threading

import Data
import FHEM

from config import config
from Frame import Frame


class UDP_Server(threading.Thread):
    """
    listen on port 5441 and receives 14 byte CoE UDP packets and stores them into a FIFO queue
    """

    __instance = None

    callback = None
    data = None
    data_frames = None
    fhem = None
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

        logging.debug(f"UDP server initiated, listening on UDP port {self.udp_port}")

    def initialize(self):
        """get needed instances from local classes"""
        self.data = Data.Data.getInstance()
        self.fhem = FHEM.FHEM.getInstance()

    def getFrames(self):
        """return frames object

        Returns:
            queue: frames object
        """
        return self.data_frames

    def run(self):
        """run the UDP_Server thread"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(("", self.udp_port))

            while True:
                data, _ = s.recvfrom(Frame.rawdataLength)
                try:
                    frame = Frame(data)
                    self.data_frames.append(frame)
                    self.sendUpdate()

                except TypeError as type_error:
                    logging.error(type_error)

    def sendFrame(self, frame):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            ip = config["udp_server"]["cmi_ip"]
            port = config["udp_server"]["cmi_port"]
            sFrame = frame.getString()

            s.sendto(frame.getData(), (ip, port))
            sFrame = frame.getString()

            logging.debug(f"sent frame {sFrame} to udp://{ip}:{port}")

    def sendUpdate(self):
        """sets update event to true"""
        if config["fhem"]["enabled"] and config["fhem"]["receiveUpdates"]:
            self.fhem.getUpdateEvent().set()