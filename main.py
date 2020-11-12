from config import config

from Data import Data
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
