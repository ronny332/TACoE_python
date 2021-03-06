import copy
import json
import logging
import os
import pickle
import threading

from collections import deque
from time import sleep, time

from config import config

import UDP_Server


class Data(threading.Thread):
    """
    data collector and formatter
    """

    __instance = None

    data_frames = deque(maxlen=config["data"]["fifo_length"])
    last = {"analogue": {}, "digital": {}}
    node_config = {"analogue": {}, "digital": {}}
    renewed = {}
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

        f"Data initiated with fifo size of {self.data_frames.maxlen} frames."

    def initialize(self):
        """get needed instances from local classes"""
        self.udp_server = UDP_Server.UDP_Server.getInstance()

        self.restore()
        self.readConfig()

    def cleanFrames(self):
        """remove all available frames from RAM and harddrive"""
        self.clearLast()
        self.data_frames.clear()
        self.save()

    def clearLast(self):
        """set the last values for analogue and digital back to None.
        self.getDifference() will return all available values at next call.
        """
        self.last["analogue"] = {}
        self.last["digital"] = {}

    def getDifference(self, analogue=False, digital=False):
        """calculates the difference between the current and last comparison.

        Args:
            analogue (bool, optional): get differences for analogue values. Defaults to False.
            digital (bool, optional): get differences for digital values. Defaults to False.

        Returns:
            dictionary: dictionary of tuples
        """
        timestamp = time()

        data = self.getValues(analogue=True) if analogue else self.getValues(digital=True)
        type = "analogue" if analogue else "digital"

        if not self.last[type]:
            self.last[type] = data
            return self.getDifference(analogue=analogue, digital=digital)
        else:
            diff = []
            for n in data:
                sNode = str(n)

                for sIndex in data[sNode].keys():
                    index_renewed = f"{sNode}-{sIndex}"
                    if index_renewed not in self.renewed:
                        self.renewed[index_renewed] = timestamp - config["data"]["renew"] - 1
                    if "value" not in data[sNode][sIndex] or "value" not in self.last[type][sNode][sIndex]:
                        continue
                    if (
                        sNode not in data
                        or data[sNode][sIndex]["value"] != self.last[type][sNode][sIndex]["value"]
                        or self.renewed[index_renewed] < timestamp - config["data"]["renew"]
                    ):
                        diff.append(
                            [
                                sNode,
                                sIndex,
                                data[sNode][sIndex]["value"],
                                self.last[type][sNode][sIndex]["value"],
                            ]
                        )
                        self.renewed[index_renewed] = timestamp
            self.last[type] = data
            return diff

    def getDumpFilename(self):
        """string of file where the saved and restored data goes to/comes from

        Returns:
            string: dump filename
        """
        return os.path.join(config["app"]["dir"], config["app"]["name"] + ".dump")

    def getFrames(self):
        """return frames object

        Returns:
            queue: frames object
        """
        return self.data_frames

    def getReadingsName(self, node, index, analogue=False, digital=False):
        """returns a matching Name, if existent

        Args:
            node (int): Node number
            index (int): Index number
            analogue (bool, optional): get name for analogue value. Defaults to False.
            digital (bool, optional): get name for digital value.. Defaults to False.

        Returns:
            [type]: [description]
        """
        type = "analogue" if analogue else "digital"

        sNode = str(node)
        sIndex = str(index)

        if (
            sNode in self.node_config[type]
            and sIndex in self.node_config[type][sNode]
            and "name" in self.node_config[type][sNode][sIndex]
        ):
            return self.node_config[type][sNode][sIndex]["name"].replace(" ", "_")

        return False

    def getValues(self, analogue=False, digital=False):
        """get values format in config declarations for digital and analogue configurations

        Args:
            analogue (bool, optional): [description]. Defaults to False.
            digital (bool, optional): [description]. Defaults to False.
            one, analogue or digital, has to be True

        Returns:
            dictionary: value dictionary of analogue or digital values
        """
        if analogue:
            return self.makeAnalogue()
        if digital:
            return self.makeDigital()

    def getRawValues(self, analogue=False, digital=False):
        """creates a data dictionary, ordered by node numbers and indexes

        Args:
            analogue (bool, optional): delivers analogue values. Defaults to False.
            digital (bool, optional): delivers digital values. Defaults to False.

        Returns:
            dictionary: data
        """
        data = {}

        for f in self.data_frames:
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

    def makeAnalogue(self):
        """create analogue representations for all available config entries

        Returns:
            dictionary: dictionary with analogue representations
        """
        data_analogue = copy.deepcopy(self.node_config["analogue"])

        for f in self.data_frames:
            if f.isDigital():
                continue

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
        return data_analogue

    def makeDigital(self):
        """create digital representations for all available config entries

        Returns:
            dictionary: dictionary with digital representations
        """
        data_digital = copy.deepcopy(self.node_config["digital"])

        for f in self.data_frames:
            sNode = str(f.getNode())
            if str(sNode) in data_digital:
                indexes = list(map(lambda i: f.getIndex(i, False), range(1, 17)))
                for i in indexes:
                    sIndex = str(i)
                    if sIndex in data_digital[sNode]:
                        value = f.getDigital(i)[2]
                        timestamp = f.getTimestamp()
                        data_digital[sNode][sIndex]["timestamp"] = timestamp
                        data_digital[sNode][sIndex]["value"] = value
        return data_digital

    def readConfig(self):
        """read config files from disc"""
        config_analogue = os.path.join(config["app"]["cwd"], "config_analogue.json")
        config_digital = os.path.join(config["app"]["cwd"], "config_digital.json")

        fn = config_analogue

        try:
            with open(fn, "r") as f:
                self.node_config["analogue"] = json.load(f)

            fn = config_digital
            with open(fn, "r") as f:
                self.node_config["digital"] = json.load(f)

            logging.info(f"read config files {config_analogue} and {config_digital}")

        except FileNotFoundError:
            logging.error(f"Config file not found ({fn})")

    def restore(self):
        """restore saved data from disc, if existent"""
        if os.path.exists(self.getDumpFilename()):
            with open(self.getDumpFilename(), "rb") as f:
                self.data_frames.clear()
                data_frames = filter(lambda df: not df.isEmpty(), pickle.load(f))

                for df in data_frames:
                    self.data_frames.append(df)
                logging.debug(f"restored {len(self.data_frames)} frames from disc")

    def run(self):
        """run the Data thread"""
        while True:
            if int(config["data"]["save"]) > 0:
                sleep(config["data"]["save"])
                self.save()
            else:
                sleep(600)
                logging.debug("No saving of frames to disc activated. Skipping.")

    def save(self):
        """save in memory data to disc"""
        with open(self.getDumpFilename(), "wb") as f:
            data_frames_list = list((filter(lambda f: not f.isEmpty(), self.data_frames)))
            pickle.dump(data_frames_list, f, protocol=pickle.HIGHEST_PROTOCOL)

            logging.debug(f"saved {len(data_frames_list)} frames to disc")

    def setFrames(self, frames):
        """sets the read/available frames data

        Args:
            frames (queue): frames data, read by UDP_Server
        """
        self.data_frames = frames
