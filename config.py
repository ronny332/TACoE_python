import logging
import os
import sys

config = {
    "app": {
        "cwd": os.path.dirname(os.path.realpath(__file__)),
        "dir": None,
        "home": os.path.join(os.path.expanduser("~"), ".config"),
        "name": "TACoE",
    },
    "control": {
        "enabled": True,
        "prompt": " > ",
        "shell": True,
        "telnet": True,
        "telnet_port": 11112,
    },
    "data": {"fifo_length": 100, "renew": 300, "save": 0},
    "debug": {"level": logging.DEBUG, "verbose": True},
    "fhem": {
        "alias": "CMI",
        "createDevice": True,
        "device": "dum_cmi",
        "enabled": False,
        "group": "Heating",
        "host": "10.0.0.23",
        "port": 7072,
        "prompt": "fhem> ",
        "receiveUpdates": True,
        "room": "devices->dummy",
        "timeout": 10,
    },
    "frame": {"bell": True, "debug": False},
    "udp_server": {"cmi_ip": "10.0.0.46", "cmi_port": 5441, "udp_port": 5441},
}


def initHomeDirectory():
    config["app"]["dir"] = f'{os.path.join(config["app"]["home"],config["app"]["name"])}'

    if not os.path.isdir(config["app"]["dir"]):
        try:
            os.makedirs(config["app"]["dir"], mode=0o755, exist_ok=True)

            if not os.access(config["app"]["dir"], os.W_OK):
                raise os.error("directory not writeable: " + config["app"]["dir"])
        except os.error:
            print("can not create directory: " + config["app"]["dir"])
            sys.exit(1)


logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=config["debug"]["level"])
logging.getLogger("asyncio").setLevel(logging.WARNING)

initHomeDirectory()
