from config import config

from Data import Data
from Shell import Shell
from UDP_Server import UDP_Server

if __name__ == "__main__":
    server = UDP_Server.getInstance()
    server.start()
    data = Data.getInstance()
    data.start()

    if config["modules"]["shell"]["enabled"]:
        shell = Shell.getInstance()
        shell.start()
