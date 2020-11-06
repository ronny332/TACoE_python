import config
from UDP_Server import UDP_Server

if __name__ == "__main__":
    # frame = bytes([53, 0, 0, 0, 0, 17, 0, 17, 18, 18, 2, 0, 0, 0, 0])

    # df = CoE_Frame(frame)
    # df.p()

    server = UDP_Server.getInstance()
    server.start()
