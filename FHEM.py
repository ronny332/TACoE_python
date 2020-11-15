import logging
import threading

from telnetlib import Telnet
from time import sleep

import Data

from config import config


class FHEM(threading.Thread):
    """
    TODO
    """

    __instance = None
    data = None
    updateEvent = threading.Event()

    @staticmethod
    def getInstance():
        """Static access method for FHEM """
        if FHEM.__instance is None:
            FHEM()
        return FHEM.__instance

    def __init__(self):
        super().__init__()

        if FHEM.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            FHEM.__instance = self

        logging.debug("FHEM initiated")

    def closeConnection(self, con):
        """closes telnet connection

        Args:
            connection (telnet connection): connection
        """
        logging.debug("closing connection")

        if con:
            con.close()

    def createDevice(self):
        """created dummy device at FHEM instance"""
        con = self.openConnection()

        if con:
            if self.isPrompt(con):
                alias = config["fhem"]["alias"]
                device = config["fhem"]["device"]
                group = config["fhem"]["group"]
                room = config["fhem"]["room"]

                cmd = f"define {device} dummy\nattr {device} event-on-change-reading .*\n"
                cmd += f"attr {device} alias {alias}\n" if alias else ""
                cmd += f"attr {device} group {group}\n" if group else ""
                cmd += f"attr {device} room {room}\n" if room else ""
                cmd += "\n"

                self.sendCommand(con, cmd)

            if self.isPrompt(con, True):
                self.closeConnection(con)

    def initialize(self):
        """get needed instances from local classes"""
        self.data = Data.Data.getInstance()

    def getUpdateEvent(self):
        """shared update event

        Returns:
            Event: update event, called bu UDP_Server
        """
        return self.updateEvent

    def isPrompt(self, con, readFirst=False):
        """read the telnet connection for FHEM Prompt

        Args:
            con (connection): telnet connection
            readFirst (bool, optional): should a earlier input been read? Defaults to False.

        Returns:
            [type]: [description]
        """
        if not con:
            return False

        if readFirst:
            s = con.get_socket()
            s.recv(32768)

        con.write(b"\n")
        r = con.read_until(bytes(config["fhem"]["prompt"], encoding="utf-8"))

        return r.decode(encoding="utf-8") == config["fhem"]["prompt"]

    def openConnection(self):
        """creates new telnet connection

        Returns:
            connection: telnet connection
        """
        host = config["fhem"]["host"]
        port = config["fhem"]["port"]

        logging.debug(f"opening telnet connection to {host}:{port}")
        return Telnet(
            host,
            port,
            timeout=config["fhem"]["timeout"],
        )

    def run(self):
        while True:
            self.updateEvent.wait()
            sleep(1.0)
            self.sendUpdates()
            self.updateEvent.clear()

    def sendCommand(self, con, cmd):
        """sends cmd over telnet conection

        Args:
            con (connection): telnet connection
            cmd (string): command
        """
        logging.debug(f"sending command: {cmd.strip()}")
        con.write(bytes(cmd + "\n\n", encoding="utf-8"))

    def sendUpdates(self):
        if config["fhem"]["createDevice"]:
            self.createDevice()
            config["fhem"]["createDevice"] = False

        # print(self.data.getDifference(analogue=True))
        # print(self.data.getDifference(digital=True))
        self.updateReadings()

    def updateReadings(self):
        """send readings to FHEM instance via telnet"""
        data_analogue = self.data.getDifference(analogue=True)
        data_digital = self.data.getDifference(digital=True)

        if len(data_analogue) or len(data_digital):
            con = self.openConnection()

            if con and self.isPrompt(con):
                device = config["fhem"]["device"]

                for d in data_analogue:
                    cmd = f"setreading {device} {self.data.getReadingsName(d[0], d[1], analogue=True)} {d[3]}"
                    self.sendCommand(con, cmd)

                    if not self.isPrompt(con, readFirst=True):
                        break

                for d in data_digital:
                    state = "on" if d[2] else "off"
                    cmd = f"setreading {device} {self.data.getReadingsName(d[0], d[1], digital=True)} {state}"
                    self.sendCommand(con, cmd)

                    if not self.isPrompt(con, readFirst=True):
                        break

                self.closeConnection(con)
