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
    print(f.setValue(21, 1, "21.2", 1, analogue=True))
    print(f.getString(True))
    f2 = Frame()
    print(f2.setValue(21, 29, True, digital=True))
    print(f2.getString(False))