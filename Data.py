import logging
import os
import pickle
import threading

from time import sleep

from config import config
from UDP_Server import UDP_Server


class Data(threading.Thread):
    """
    data collector and formatter
    """

    __instance = None

    frames = None
    udp_server = None

    @staticmethod
    def getInstance():
        """Static access method for Data """
        if Data.__instance is None:
            Data()
        return Data.__instance

    def __init__(self):
        super().__init__()

        if Data.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            Data.__instance = self

        self.udp_server = UDP_Server.getInstance()
        self.frames = self.udp_server.getFrames()

        self.restore()

    def getDumpFilename(self):
        """string of file where the saved and restored data goes to/comes from

        Returns:
            string: dump filename
        """
        return os.path.join(config["app"]["dir"], config["app"]["name"] + '.dump')

    def run(self):
        """run the Data thread
        """
        while True:
            sleep(config["modules"]["data"]["save"])
            self.save()

    def restore(self):
        """restore saved data from disc, if existent
        """
        if os.path.exists(self.getDumpFilename()):
            with open(self.getDumpFilename(), 'rb') as f:
                self.frames.clear()
                frames = pickle.load(f)

                for f in frames:
                    self.frames.append(f)
                logging.debug(f'restored {len(self.frames)} frames from disc')

    def save(self):
        """save in memory data to disc
        """
        with open(self.getDumpFilename(), 'wb') as f:
            pickle.dump(self.frames, f, protocol=pickle.HIGHEST_PROTOCOL)

            logging.debug(f'saved {len(self.frames)} frames to disc')

    def setFrames(self, frames):
        """sets the read/available frames data

        Args:
            frames (queue): frames data, read by UDP_Server
        """
        self.frames = frames
