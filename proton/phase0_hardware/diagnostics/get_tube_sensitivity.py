"""
Reads GET tubeSensitivity from the GC-01.

Sensitivity is the bridge between counts and dose. It comes back in cpm per
uSv/h. This script reads it, then shows what a few example count rates would
convert to, so you can sanity check it against the value printed on the listing
or the Rad Pro default before trusting it in the rest of the pipeline.

    python get_tube_sensitivity.py --port /dev/ttyACM0
"""

import sys
import argparse

sys.path.insert(0, __import__("os").path.abspath(
    __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "..")
))

from proton.common.radpro_serial import RadProDevice, RadProError, find_likely_ports
from proton.common.units import all_units


def resolve_port(requested):
    if requested:
        return requested
    ports = find_likely_ports()
    if not ports:
        return None
    return ports[0]["device"]


def main():
    parser = argparse.ArgumentParser(description="Read GC-01 tube sensitivity")
    parser.add_argument("--port", help="Serial port. If omitted, uses first found.")
    args = parser.parse_args()

    port = resolve_port(args.port)
    if port is None:
        print("No serial ports found. Plug in the device with a data cable.")
        return 1

    try:
        with RadProDevice(port) as dev:
            sensitivity = dev.get_tube_sensitivity()
    except RadProError as e:
        print("Could not read sensitivity: {}".format(e))
        return 1
    except Exception as e:
        print("Serial problem on {}: {}".format(port, e))
        return 1

    print("Connected on {}".format(port))
    print("Tube sensitivity: {:.3f} cpm per uSv/h".format(sensitivity))
    print("")
    print("This is the conversion constant the whole pipeline will use.")
    print("Example conversions at this sensitivity:")
    print("")
    print("  {:>10}  {:>10}  {:>12}  {:>12}  {:>12}".format(
        "CPM", "CPS", "uSv/h", "uGy/h", "mR/h"))
    for cpm in [20, 60, 120, 300, 1000]:
        u = all_units(cpm, sensitivity)
        print("  {:>10.1f}  {:>10.3f}  {:>12.5f}  {:>12.5f}  {:>12.6f}".format(
            u["cpm"], u["cps"], u["usv_h"], u["ugy_h"], u["mr_h"]))

    print("")
    print("If this sensitivity does not match what you expect, check which")
    print("calibration source it assumes. The listing quotes 80 cpm/uSv/h for")
    print("Co-60, the Rad Pro GC-01 default is often near 153.8 cpm/uSv/h.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
