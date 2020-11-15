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
    f.setValue(31, 9, "47.8", 1, analogue=True)
    f.setValue(31, 10, "57.8", 1, analogue=True)
    f.setValue(31, 11, "67.8", 1, analogue=True)
    f.setValue(31, 12, "87.8", 1, analogue=True)
    print(f.getString(verbose=False))

    f2 = Frame()
    f2.setValue(21, 1, True, digital=True)
    f2.setValue(21, 2, True, digital=True)
    f2.setValue(21, 3, True, digital=True)
    f2.setValue(21, 4, True, digital=True)
    f2.setValue(21, 3, False, digital=True)
    print(f2.getString(verbose=True))

    f3 = Frame()
    f3.setValue(21, 17, True, digital=True)
    f3.setValue(21, 18, True, digital=True)
    f3.setValue(21, 19, True, digital=True)
    f3.setValue(21, 20, True, digital=True)
    f3.setValue(21, 17, False, digital=True)

    f3.setValue(21, 21, True, digital=True)
    f3.setValue(21, 22, True, digital=True)
    f3.setValue(21, 23, True, digital=True)
    f3.setValue(21, 24, True, digital=True)
    f3.setValue(21, 22, False, digital=True)
    print(f3.getString(verbose=True))