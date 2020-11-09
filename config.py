import logging
import os
import sys

config = {
    "app": {
        "dir": None,
        "home": os.path.join(os.path.expanduser("~"), '.config'),
        "name": "TACoE"
    },
    "debug": {
        "level": logging.DEBUG,
        "verbose": True
    },
    "modules": {
        "coe_frame": {
            "bell": True,
            "debug": False
        },
        "data": {
            "save": 300
        },
        "shell": {
            "enabled": True
        }
    },
    "udp_server": {
        "fifo_length": 100,
        "udp_port": 5441
    }
}


def initHomeDirectory():
    config["app"]["dir"] = f'{os.path.join(config["app"]["home"],config["app"]["name"])}'

    if not os.path.isdir(config["app"]["dir"]):
        try:
            os.makedirs(config["app"]["dir"], mode=0o755, exist_ok=True)

            if not os.access(config["app"]["dir"], os.W_OK):
                raise os.error('directory not writeable: ' + config["app"]["dir"])
        except os.error:
            print('can not create directory: ' + config["app"]["dir"])
            sys.exit(1)


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=config["debug"]['level']
)

logging.getLogger('asyncio').setLevel(logging.WARNING)

initHomeDirectory()