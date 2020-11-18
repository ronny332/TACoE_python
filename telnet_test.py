# from telnetlib import Telnet

# t = Telnet(host="10.0.0.23", port=7072, timeout=10)
# t.write(b"\n")

# r = t.read_until(b"fhem> ")
# t.close()
# print(r)

import re

# https://regex101.com/r/Kr6CeS/1

r = re.compile(
    r"^(?:s|save)\s((?P<analogue>a)|(?P<digital>d))\s(?P<node>[0-9]+)\s(?P<index>[0-9]+)\s(?(analogue)(?P<aValue>[0-9.]+)|(?P<dValue>[0-1]))\s?(?(analogue)(?P<decimals>[0-9])+)$"
)
print(r.match("save a 41 12 67.2 1").groupdict())
