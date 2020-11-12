import logging
import threading

import Data


class Telnet(threading.Thread):
    """
    TODO
    """

    __instance = None
    data = None
    updateEvent = threading.Event()

    @staticmethod
    def getInstance():
        """Static access method for Telnet """
        if Telnet.__instance is None:
            Telnet()
        return Telnet.__instance

    def __init__(self):
        super().__init__()

        if Telnet.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            Telnet.__instance = self

        logging.debug("Telnet initiated")

    def initialize(self):
        """get needed instances from local classes"""
        self.data = Data.Data.getInstance()

    def getUpdateEvent(self):
        return self.updateEvent

    def run(self):
        while True:
            self.updateEvent.wait()
            print("Got update.")
            self.updateEvent.clear()