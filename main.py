from config import config

from Data import Data
from Shell import Shell
from UDP_Server import UDP_Server

if __name__ == "__main__":
    threads = {"data": Data.getInstance(), "server": UDP_Server.getInstance()}

    if config["modules"]["shell"]["enabled"]:
        threads["shell"] = Shell.getInstance()

    for _, t in threads.items():
        t.start()
