import logging


class CoE_Types(object):
    """
    CoE Types class
    """

    __instance = None

    @staticmethod
    def getInstance():
        """Static access method for CoE_Types """
        if CoE_Types.__instance is None:
            CoE_Types()
        return CoE_Types.__instance

    units = {
        0: (0, 'None', ''),
        1: (1, 'Temperature', '°C'),
        4: (0, 'Seconds', 's'),
        10: (1, 'KiloWatt', 'kW'),
        11: (1, 'KiloWattHours', 'kWh'),
        12: (0, 'MegaWattHours', 'MWh'),
        23: (2, 'Pressure', 'Bar')
    }

    def __init__(self):
        super().__init__()

        if CoE_Types.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            CoE_Types.__instance = self

        logging.debug('Types initialized')

    def getTypeDetails(self, unit):
        """return a dictionary for given unit number

        Args:
            unit (int): number of unit

        Raises:
            TypeError: failure on invalid unit number

        Returns:
            dictionary: details for given unit number
        """
        if self.units.get(unit, None) is None:
            raise TypeError(f'{unit} is not a valid unit')

        return {
            'decimals': self.units[unit],
            'name': self.units[unit],
            'unit': self.units[unit]
        }
