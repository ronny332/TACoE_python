import copy
import json
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

    config = {"analogue": None, "digital": None}
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
        self.readConfig()

    def getDumpFilename(self):
        """string of file where the saved and restored data goes to/comes from

        Returns:
            string: dump filename
        """
        return os.path.join(config["app"]["dir"], config["app"]["name"] + ".dump")

    def getValues(self, analogue=False, digital=False):
        data_analogue = None
        data_digital = None

        if analogue:
            data_analogue = copy.deepcopy(self.config["analogue"])

            for f in self.frames:
                sNode = str(f.getNode())
                if str(sNode) in data_analogue:
                    indexes = list(map(lambda i: (i, str(f.getIndex(i))), range(1, 5)))
                    for i in indexes:
                        if i[1] in data_analogue[sNode]:
                            decimals = int(data_analogue[sNode][i[1]]["decimals"])
                            raw = f.getAnalogue(i[0])[2]
                            timestamp = f.getTimestamp()
                            unit = data_analogue[sNode][i[1]]["unit"]
                            value = raw / pow(10, decimals)
                            value_unit = f"{value} {unit}"

                            data_analogue[sNode][i[1]]["raw"] = raw
                            data_analogue[sNode][i[1]]["timestamp"] = timestamp
                            data_analogue[sNode][i[1]]["value"] = value
                            data_analogue[sNode][i[1]]["value_unit"] = value_unit
        if digital:
            data_digital = copy.deepcopy(self.config["digital"])

        return (data_analogue, data_digital)

    def getRawValues(self, analogue=False, digital=False):
        """creates a data dictionary, ordered by node numbers and indexes

        Args:
            analogue (bool, optional): delivers analogue values. Defaults to False.
            digital (bool, optional): delivers digital values. Defaults to False.

        Returns:
            dictionary: data
        """
        data = {}

        for f in self.frames:
            if f.isAnalogue() and analogue:
                node = f.getNode()
                if node not in data:
                    data[node] = {}
                for i in range(1, 5):
                    index = f.getIndex(i, analogue=True)
                    data[node][index] = f.getAnalogue(i)

            if f.isDigital() and digital:
                node = f.getNode()
                if node not in data:
                    data[node] = {}
                for i in range(1, 33):
                    index = f.getIndex(i, analogue=False)
                    data[node][index] = f.getDigital(i)

        return data

    def readConfig(self):
        """read config files from disc"""
        config_analogue = "config_analogue.json"
        config_digital = "config_digital.json"

        fn = config_analogue

        try:
            with open(fn, "r") as f:
                self.config["analogue"] = json.load(f)

            fn = config_digital
            with open(fn, "r") as f:
                self.config["digital"] = json.load(f)

            logging.info(f"read config files {config_analogue} and {config_digital}")

        except FileNotFoundError:
            logging.error(f"Config file not found ({fn})")

    def restore(self):
        """restore saved data from disc, if existent"""
        if os.path.exists(self.getDumpFilename()):
            with open(self.getDumpFilename(), "rb") as f:
                self.frames.clear()
                frames = pickle.load(f)

                for f in frames:
                    self.frames.append(f)
                logging.debug(f"restored {len(self.frames)} frames from disc")

    def run(self):
        """run the Data thread"""
        while True:
            sleep(config["modules"]["data"]["save"])
            self.save()

    def save(self):
        """save in memory data to disc"""
        with open(self.getDumpFilename(), "wb") as f:
            pickle.dump(self.frames, f, protocol=pickle.HIGHEST_PROTOCOL)

            logging.debug(f"saved {len(self.frames)} frames to disc")

    def setFrames(self, frames):
        """sets the read/available frames data

        Args:
            frames (queue): frames data, read by UDP_Server
        """
        self.frames = frames
