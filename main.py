from config import config

from Data import Data
from Frame import Frame
from FHEM import FHEM
from Shell import Shell
from UDP_Server import UDP_Server

if __name__ == "__main__":
    threads = {"data": Data.getInstance(), "server": UDP_Server.getInstance()}

    if config["modules"]["fhem"]["enabled"]:
        threads["fhem"] = FHEM.getInstance()
    if config["modules"]["shell"]["enabled"]:
        threads["shell"] = Shell.getInstance()

    for _, t in threads.items():
        t.start()
        t.initialize()

    f = Frame()
    print(f.isEmpty())
    print(f.isMutable())
    print(f.setValue(22, 1, "47.8", 1, analogue=True))
    print(f.setValue(22, 2, "57.8", 1, analogue=True))
    # print(f.setValue(22, 3, "67.8", 1, analogue=True))
    print(f.setValue(22, 4, "87.8", 1, analogue=True))
    print(f.getString(True))
    f2 = Frame()
    print(f2.setValue(21, 29, True, digital=True))
    print(f2.getString(False))