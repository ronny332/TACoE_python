from config import config

from Control import Control
from Data import Data
from Frame import Frame
from FHEM import FHEM
from UDP_Server import UDP_Server

if __name__ == "__main__":
    threads = {"data": Data.getInstance(), "udp_server": UDP_Server.getInstance()}

    if config["control"]["enabled"]:
        threads["control"] = Control.getInstance()
    if config["fhem"]["enabled"]:
        threads["fhem"] = FHEM.getInstance()

    for _, t in threads.items():
        t.start()
        t.initialize()

    # f = Frame()
    # print(f.isEmpty())
    # print(f.isMutable())
    # f.setValue(31, 9, "52.1", 1, analogue=True)
    # f.setValue(31, 10, "57.8", 1, analogue=True)
    # f.setValue(31, 11, "67.8", 1, analogue=True)
    # f.setValue(31, 12, "87.8", 1, analogue=True)
    # print(f.getString(verbose=False))

    # threads["udp_server"].sendFrame(f)

    # f2 = Frame()
    # f2.setValue(41, 1, True, digital=True)
    # f2.setValue(41, 2, True, digital=True)
    # f2.setValue(41, 3, True, digital=True)
    # f2.setValue(41, 4, True, digital=True)
    # f2.setValue(41, 3, False, digital=True)
    # print(f2.getString(verbose=True))

    # threads["udp_server"].sendFrame(f2)

    # f3 = Frame()
    # f3.setValue(41, 17, True, digital=True)
    # f3.setValue(41, 18, True, digital=True)
    # f3.setValue(41, 19, True, digital=True)
    # f3.setValue(41, 20, True, digital=True)
    # f3.setValue(41, 17, False, digital=True)

    # f3.setValue(41, 21, True, digital=True)
    # f3.setValue(41, 22, True, digital=True)
    # f3.setValue(41, 23, True, digital=True)
    # f3.setValue(41, 24, True, digital=True)
    # f3.setValue(41, 22, False, digital=True)
    # print(f3.getString(verbose=True))

    # threads["udp_server"].sendFrame(f2)