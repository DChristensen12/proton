"""
Live monitor for the GC-01.

Polls the device on a fixed interval and prints the count rate in every unit
the display can show. It derives a true measured rate from the difference in
cumulative pulse count between polls, which is more honest than the firmware
rate field because you can see exactly what window it covers.

This is the hand operated cousin of the Phase 1 logger. Use it to watch the
device respond when you bring a check source near it, before you wire up any
machine learning.

    python live_monitor.py --port /dev/ttyACM0 --interval 1.0
"""

import sys
import time
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
    parser = argparse.ArgumentParser(description="Live GC-01 monitor")
    parser.add_argument("--port", help="Serial port. If omitted, uses first found.")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between polls (default 1.0)")
    args = parser.parse_args()

    port = resolve_port(args.port)
    if port is None:
        print("No serial ports found. Plug in the device with a data cable.")
        return 1

    try:
        with RadProDevice(port) as dev:
            sensitivity = dev.get_tube_sensitivity()
            print("Connected on {}, sensitivity {:.3f} cpm/uSv/h".format(port, sensitivity))
            print("Polling every {:.2f}s. Press Ctrl-C to stop.".format(args.interval))
            print("")
            print("  {:>8}  {:>8}  {:>9}  {:>10}  {:>10}  {:>10}".format(
                "counts", "d_count", "CPM(meas)", "uSv/h", "CPS", "mR/h"))

            prev_count = dev.get_tube_pulse_count()
            prev_time = time.monotonic()

            while True:
                time.sleep(args.interval)
                now_count = dev.get_tube_pulse_count()
                now_time = time.monotonic()

                elapsed = now_time - prev_time
                d_count = now_count - prev_count
                # Guard against the lifetime counter overflowing back to zero.
                if d_count < 0:
                    d_count = 0
                measured_cpm = (d_count / elapsed) * 60.0 if elapsed > 0 else 0.0

                u = all_units(measured_cpm, sensitivity)
                print("  {:>8d}  {:>8d}  {:>9.1f}  {:>10.5f}  {:>10.3f}  {:>10.6f}".format(
                    now_count, d_count, u["cpm"], u["usv_h"], u["cps"], u["mr_h"]))

                prev_count = now_count
                prev_time = now_time

    except KeyboardInterrupt:
        print("")
        print("Stopped.")
        return 0
    except RadProError as e:
        print("Device error: {}".format(e))
        return 1
    except Exception as e:
        print("Serial problem: {}".format(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
