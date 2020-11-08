import logging

config = {
    "debug": {
        "level": logging.DEBUG,
        "long": True
    }
}

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=config["debug"]['level']
)
