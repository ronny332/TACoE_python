import json
import multiprocessing
import os
import re
import threading

from time import sleep

import Data
import UDP_Server

from Frame import Frame


class Shell(threading.Thread):
    """
    input/output from a shell like interface
    """

    __instance = None
    cmds = {"send": None}
    data = None
    data_frames = None

    @staticmethod
    def getInstance():
        """Static access method for Shell """
        if Shell.__instance is None:
            Shell()
        return Shell.__instance

    def __init__(self):
        super().__init__()

        if Shell.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            Shell.__instance = self

    def initialize(self):
        """get needed instances from local classes"""
        self.data = Data.Data.getInstance()
        self.data_frames = self.data.getFrames()

    def command(self, cmd):
        if len(self.data_frames) > 0:
            if cmd in ["a", "analogue"]:
                print(json.dumps(self.data.getValues(analogue=True)))
            elif cmd in ["c", "clean"]:
                self.data.cleanFrames()
                print("OK")
            elif cmd in ["d", "digital"]:
                print(json.dumps(self.data.getValues(digital=True)))
            elif cmd in ["da", "diff analogue"]:
                print(json.dumps(self.data.getDifference(analogue=True)))
            elif cmd in ["dd", "diff digital"]:
                print(json.dumps(self.data.getDifference(digital=True)))
            elif cmd in ["ar", "analogue raw"]:
                print(json.dumps(self.data.getRawValues(analogue=True)))
            elif cmd in ["dr", "digital raw"]:
                print(json.dumps(self.data.getRawValues(digital=True)))
            elif cmd in ["f", "frames"]:
                for f in reversed(self.data_frames):
                    print(f.getString(verbose=True))
                print(f"({len(self.data_frames)} frames)")
            elif cmd in ["h", "help"]:
                print(
                    "\n".join(
                        [
                            "\ta(analogue):\t\tall analogue values (JSON)",
                            "\td(digital):\t\tall digital values (JSON)",
                            "\tar(analogue):\t\tall analogue raw values (JSON)",
                            "\tda(diff analogue):\tdifferences of analogue values since last call (JSON)",
                            "\tdd(diff digital):\tdifferences of digital values since last call (JSON)",
                            "\tdr(digital):\t\tall digital raw values (JSON)",
                            "\tf(frames):\t\tshow all available frames",
                            "\th(help):\t\tshow this help",
                            "\tlf(last frame):\t\tshow last frame",
                            "\tr(restore):\t\trestore saved frames",
                            "\ts(send):\t\tsend command",
                            "\tw(write):\t\\write available frames to disc",
                        ]
                    )
                )
            elif cmd in ["q", "quit"]:
                os._exit(1)
            elif cmd in ["lf", "last frame"]:
                print(f"{self.data_frames[-1].getString(verbose=True)}")
            elif cmd in ["r", "restore"]:
                self.data.restore()
            elif cmd.startswith("s ") or cmd.startswith("send "):
                try:
                    self.send(cmd)
                except ValueError as e:
                    print(e)
            elif cmd in ["w", "write"]:
                self.data.save()
            else:
                print("invalid command")
        else:
            print("no frames, need to wait for new input.")

    def run(self):
        """run the Shell thread"""
        while True:
            self.command(input("  > "))

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
