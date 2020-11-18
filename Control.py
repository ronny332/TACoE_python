import json
import logging
import os
import re
import socket
import sys
import threading

from concurrent import futures
from time import sleep

import Data
import UDP_Server

from config import config
from Frame import Frame


class Control(threading.Thread):
    """
    input/output from a shell/telnet like interface
    """

    __instance = None
    cmds = {"send": None}
    data = None
    data_frames = None
    executor = futures.ThreadPoolExecutor(max_workers=2)

    @staticmethod
    def getInstance():
        """Static access method for Control """
        if Control.__instance is None:
            Control()
        return Control.__instance

    def __init__(self):
        super().__init__()

        if Control.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            Control.__instance = self

        logging.debug("Control initiated")

    def initialize(self):
        """get needed instances from local classes"""
        self.data = Data.Data.getInstance()
        self.data_frames = self.data.getFrames()

    def command(self, cmd, write_to_stream):
        """command switcher

        Args:
            cmd (str): command to run
            write_to_stream ([func): function to write output to
        """
        if cmd in ["q", "quit"]:
            res = "quit."
            if write_to_stream is print:
                print(res)
                os._exit(0)
            else:
                write_to_stream(res)
        elif cmd in ["h", "help"]:
            write_to_stream(
                "\n".join(
                    [
                        "Command         [long command] Description",
                        "----------------------------------------------------------------------",
                        "  a\t\t[analogue] all analogue values (JSON)",
                        "  d\t\t[digital] all digital values (JSON)",
                        "  ar\t\t[analogue] all analogue raw values (JSON)",
                        "  da\t\t[diff analogue] differences of analogue values since last call (JSON)",
                        "  dd\t\t[diff digital] differences of digital values since last call (JSON)",
                        "  dr\t\t[digital] all digital raw values (JSON)",
                        "  f\t\t[frames] show all available frames",
                        "  h\t\t[help] tshow this help",
                        "  lf\t\t[last frame):\t\tshow last frame",
                        "  r\t\t[restore] restore saved frames",
                        "  s\t\t[send] send command",
                        "  w\t\t[write] write available frames to disc",
                    ]
                )
            )
        elif len(self.data_frames) > 0:
            if cmd in ["a", "analogue"]:
                write_to_stream(json.dumps(self.data.getValues(analogue=True)))
            elif cmd in ["c", "clean"]:
                self.data.cleanFrames()
                write_to_stream("OK.")
            elif cmd in ["d", "digital"]:
                write_to_stream(json.dumps(self.data.getValues(digital=True)))
            elif cmd in ["da", "diff analogue"]:
                write_to_stream(json.dumps(self.data.getDifference(analogue=True)))
            elif cmd in ["dd", "diff digital"]:
                write_to_stream(json.dumps(self.data.getDifference(digital=True)))
            elif cmd in ["ar", "analogue raw"]:
                write_to_stream(json.dumps(self.data.getRawValues(analogue=True)))
            elif cmd in ["dr", "digital raw"]:
                write_to_stream(json.dumps(self.data.getRawValues(digital=True)))
            elif cmd in ["f", "frames"]:
                for f in reversed(self.data_frames):
                    write_to_stream(f.getString(verbose=True))
                write_to_stream(f"({len(self.data_frames)} frames)")
            elif cmd in ["lf", "last frame"]:
                write_to_stream(f"{self.data_frames[-1].getString(verbose=True)}")
            elif cmd in ["r", "restore"]:
                self.data.restore()
                write_to_stream("OK.")
            elif cmd.startswith("s ") or cmd.startswith("send "):
                try:
                    self.send(cmd)
                    write_to_stream("OK.")
                except ValueError as e:
                    write_to_stream(e)
            elif cmd in ["w", "write"]:
                self.data.save()
                write_to_stream("OK.")
            else:
                write_to_stream("invalid command.")
        else:
            write_to_stream("no frames, need to wait for new input.")

    def run(self):
        """run the Control thread"""
        if config["control"]["shell"]:
            self.executor.submit(self.run_shell)
        if config["control"]["telnet"]:
            self.executor.submit(self.run_telnet)

        self.executor.shutdown(wait=False)

    def run_shell(self):
        """shell thread"""
        sleep(1)
        logging.debug("Control/Shell initialized.")

        while True:
            self.command(input(config["control"]["prompt"]), print)

    def run_telnet(self):
        """telnet thread"""
        try:
            with socket.create_server(("", config["control"]["telnet_port"])) as s:
                s.listen(1)
                logging.debug("Control/Telnet initialized, listening on port udp://:" + str(config["control"]["telnet_port"]) + ".")

                while True:
                    conn, _ = s.accept()

                    def write_to_stream(res):
                        if res:
                            if res == "quit.":
                                conn.send((res + "\r\n").encode())
                                conn.close()
                            else:
                                lines = str(res).split("\n")
                                for l in lines:
                                    conn.send((l + "\r\n").encode())
                                conn.send(config["control"]["prompt"].encode())

                    while conn.fileno() > 0:
                        data = conn.recv(1024)

                        if not data:
                            conn.close()

                        self.command(data.decode("utf-8").strip(), write_to_stream)
        except Exception as e:
            logging.error(e)

    def send(self, cmd):
        if self.cmds["send"] is None:
            self.cmds["send"] = re.compile(
                r"^(?:s|save)\s((?P<analogue>a)|(?P<digital>d))\s"
                r"(?P<node>[0-9]+)\s(?P<index>[0-9]+)\s"
                r"(?(analogue)(?P<aValue>[0-9.]+)|(?P<dValue>[0-1]))\s?"
                r"(?(analogue)(?P<decimals>[0-9])+)$"
            )

        if not self.send_command(cmd):
            raise ValueError('command has wrong syntax. use e.g. "send a 54 15 22.3 1" for analogue requests.')

    def send_command(self, cmd):
        if self.cmds["send"]:
            m = self.cmds["send"].match(cmd)
            if m:
                print(m.groupdict())

                analogue = m.group("analogue") == "a"
                digital = not analogue

                print(analogue, digital)

                return True

        return False
