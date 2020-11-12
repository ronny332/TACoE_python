import json
import multiprocessing
import os
import threading

from time import sleep

from Data import Data
from UDP_Server import UDP_Server


class Shell(threading.Thread):
    """
    input/output from a shell like interface
    """

    __instance = None
    data = None
    frames = None
    udp_server = None

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

        self.data = Data.getInstance()
        self.udp_server = UDP_Server.getInstance()
        self.frames = self.udp_server.getFrames()

    def command(self, cmd):
        if len(self.frames) > 0:
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
                for f in reversed(self.frames):
                    print(f.getString(verbose=True))
                print(f"({len(self.frames)} frames)")
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
                            "\ts(save):\t\tsave available frames",
                        ]
                    )
                )
            elif cmd in ["q", "quit"]:
                os._exit(1)
            elif cmd in ["lf", "last frame"]:
                print(f"{self.frames[-1].getString(verbose=True)}")
            elif cmd in ["r", "restore"]:
                self.data.restore()
            elif cmd in ["s", "save"]:
                self.data.save()
            else:
                print("invalid command")
        else:
            print("no frames, need to wait for new input.")

    def run(self):
        """run the Shell thread"""
        while True:
            self.command(input("  > "))
