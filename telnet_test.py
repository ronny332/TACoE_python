from telnetlib import Telnet

t = Telnet(host="10.0.0.23", port=7072, timeout=10)
t.write(b"\n")

r = t.read_until(b"fhem> ")
t.close()
print(r)
