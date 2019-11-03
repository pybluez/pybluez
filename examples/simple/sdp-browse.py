#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyBluez simple example sdp-browse.py

Displays services being advertised on a specified bluetooth device.

Author: Albert Huang <albert@csail.mit.edu>
$Id: sdp-browse.py 393 2006-02-24 20:30:15Z albert $
"""

import sys
import bluetooth

if len(sys.argv) < 2:
    print("Usage: sdp-browse.py <addr>")
    print("   addr - can be a bluetooth address, \"localhost\", or \"all\"")
    sys.exit(2)

target = sys.argv[1]
if target == "all":
    target = None

services = bluetooth.find_service(address=target)

if len(services) > 0:
    print("Found {} services on {}.".format(len(services), sys.argv[1]))
else:
    print("No services found.")

for svc in services:
    print("\nService Name: {}".format(svc["name"]))
    print("    Host:        {}".format(svc["host"]))
    print("    Description: {}".format(svc["description"]))
    print("    Provided By: {}".format(svc["provider"]))
    print("    Protocol:    {}".format(svc["protocol"]))
    print("    channel/PSM: {}".format(svc["port"]))
    print("    svc classes: {}".format(svc["service-classes"]))
    print("    profiles:    {}".format(svc["profiles"]))
    print("    service id:  {}".format(svc["service-id"]))
