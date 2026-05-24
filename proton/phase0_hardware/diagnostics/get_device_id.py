"""
Reads GET deviceId from the GC-01.

This is the first thing to run after flashing Rad Pro and turning on Data Mode.
It confirms the laptop can see the device, the port is right, and the firmware
is talking. Run it with no arguments to auto scan ports, or pass a port:

    python get_device_id.py
    python get_device_id.py --port /dev/ttyACM0
    python get_device_id.py --port COM5
"""

import sys
import argparse

# Make the proton package importable when running this file directly.
sys.path.insert(0, __import__("os").path.abspath(
    __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "..")
))

from proton.common.radpro_serial import RadProDevice, RadProError, find_likely_ports


def parse_device_id(raw):
    """
    Split the deviceId reply into its three parts.

    The reply looks like hardware-id;software-id;device-id, for example
    FNIRSI GC-01 (CH32F103R8);Rad Pro 2.0/en;b5706d937087f975b5812810
    """
    parts = raw.split(";")
    fields = {"hardware_id": "", "software_id": "", "device_id": ""}
    if len(parts) > 0:
        fields["hardware_id"] = parts[0].strip()
    if len(parts) > 1:
        fields["software_id"] = parts[1].strip()
    if len(parts) > 2:
        fields["device_id"] = parts[2].strip()
    return fields


def try_port(port):
    """Attempt to read the device id from one port. Returns fields or None."""
    try:
        with RadProDevice(port) as dev:
            raw = dev.get_device_id()
            return parse_device_id(raw)
    except (RadProError, Exception):
        return None


def main():
    parser = argparse.ArgumentParser(description="Read GC-01 device identification")
    parser.add_argument("--port", help="Serial port. If omitted, scans all ports.")
    args = parser.parse_args()

    if args.port:
        candidates = [args.port]
    else:
        ports = find_likely_ports()
        if not ports:
            print("No serial ports found. Is the device plugged in with a data cable?")
            print("On the GC-01, also check that Data Mode is toggled ON in settings.")
            return 1
        print("Found these serial ports, trying each one:")
        for p in ports:
            print("  {}  {}".format(p["device"], p["description"]))
        candidates = [p["device"] for p in ports]

    for port in candidates:
        fields = try_port(port)
        if fields is not None:
            print("")
            print("Connected on {}".format(port))
            print("  Hardware: {}".format(fields["hardware_id"]))
            print("  Software: {}".format(fields["software_id"]))
            print("  Device id: {}".format(fields["device_id"]))
            return 0

    print("")
    print("Could not get a device id from any port.")
    print("Checklist: data cable not charge-only, Data Mode ON, device powered on.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
