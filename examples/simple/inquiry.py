# file: inquiry.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: performs a simple device inquiry followed by a remote name request of
#       each discovered device
# $Id: inquiry.py 401 2006-05-05 19:07:48Z albert $
#

import bluetooth

print("performing inquiry...")

nearby_devices = bluetooth.discover_devices(
        duration=8, lookup_names=True, flush_cache=True, lookup_class=False)

print("found %d devices" % len(nearby_devices))

for addr, name in nearby_devices:
    try:
        print("  %s - %s" % (addr, name))
    except UnicodeEncodeError:
        print("  %s - %s" % (addr, name.encode('utf-8', 'replace')))

