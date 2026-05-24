"""
Probes every readable capability of the GC-01 over the Rad Pro protocol.

This walks the full command set from the protocol doc and reports, for each one,
whether your specific device supports it and what it returns. Some commands are
marked supported-devices-only in the docs (HV frequency, HV duty cycle, electric
field, magnetic field) and will likely come back as ERROR on the GC-01. That is
expected and gets reported as not supported rather than crashing.

Run this once after flashing so you have a clear inventory of what data the
device can actually give you, which is the honest basis for the later phases.

    python probe_capabilities.py --port /dev/ttyACM0
"""

import sys
import time
import argparse

sys.path.insert(0, __import__("os").path.abspath(
    __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "..", "..")
))

from proton.common.radpro_serial import RadProDevice, RadProError, find_likely_ports


def resolve_port(requested):
    if requested:
        return requested
    ports = find_likely_ports()
    if not ports:
        return None
    return ports[0]["device"]


# Each entry is a label, the method to call, and a short note on what it means.
# The method takes the device and returns a printable value.
PROBES = [
    ("Device identification", lambda d: d.get_device_id(),
     "hardware, firmware version, unique id"),
    ("Battery voltage (V)", lambda d: d.get_battery_voltage(),
     "all cells combined"),
    ("Device time (unix)", lambda d: d.get_device_time(),
     "device clock, set this correctly for datalog timestamps"),
    ("Device timezone (h)", lambda d: d.get_device_timezone(),
     "offset from UTC"),
    ("Tube lifetime (s)", lambda d: d.get_tube_time(),
     "how long the tube has been running"),
    ("Cumulative pulse count", lambda d: d.get_tube_pulse_count(),
     "lifetime counts, the finest grained real time signal available"),
    ("Instantaneous rate (CPM)", lambda d: d.get_tube_rate(),
     "firmware computed, updated once per second"),
    ("Tube sensitivity (cpm/uSv/h)", lambda d: d.get_tube_sensitivity(),
     "counts to dose conversion constant"),
    ("Tube dead time (s)", lambda d: d.get_tube_dead_time(),
     "upper bound, matters at high count rates"),
    ("Dead time compensation (s)", lambda d: d.get_tube_dead_time_compensation(),
     "zero if disabled"),
    ("HV PWM frequency (Hz)", lambda d: d.get_tube_hv_frequency(),
     "supported devices only, may be ERROR on GC-01"),
    ("HV PWM duty cycle", lambda d: d.get_tube_hv_duty_cycle(),
     "supported devices only, may be ERROR on GC-01"),
    ("Electric field (V/m)", lambda d: d.get_electric_field(),
     "supported devices only, may be ERROR on GC-01"),
    ("Magnetic field (T)", lambda d: d.get_magnetic_field(),
     "supported devices only, may be ERROR on GC-01"),
    ("Random data (hex)", lambda d: d.get_random_data(),
     "hardware random from decay timing, up to 16 bytes"),
]


def run_probe(dev, label, fn, note):
    """Run one probe and return a result row."""
    try:
        value = fn(dev)
        return (label, "ok", str(value), note)
    except RadProError:
        return (label, "not supported", "device returned ERROR or no reply", note)
    except Exception as e:
        return (label, "error", str(e), note)


def check_datalog(dev):
    """Datalog is its own thing because the reply can be large."""
    try:
        # Ask for at most a few recent records so we do not dump the whole flash.
        raw = dev.get_datalog(max_records=5)
        record_chunks = [c for c in raw.split(";") if c]
        # The first chunk is the header row of field names.
        header = record_chunks[0] if record_chunks else ""
        sample_count = max(0, len(record_chunks) - 1)
        summary = "header [{}], {} sample record(s) returned".format(header, sample_count)
        return ("On-device datalog", "ok", summary,
                "stored time and cumulative count pairs, roughly 60s apart")
    except RadProError:
        return ("On-device datalog", "not supported",
                "device returned ERROR, datalog may be empty or disabled", "")
    except Exception as e:
        return ("On-device datalog", "error", str(e), "")


def main():
    parser = argparse.ArgumentParser(description="Probe all GC-01 capabilities")
    parser.add_argument("--port", help="Serial port. If omitted, uses first found.")
    args = parser.parse_args()

    port = resolve_port(args.port)
    if port is None:
        print("No serial ports found. Plug in the device with a data cable.")
        return 1

    print("Probing GC-01 on {}".format(port))
    print("=" * 70)

    results = []
    try:
        with RadProDevice(port) as dev:
            for label, fn, note in PROBES:
                results.append(run_probe(dev, label, fn, note))
                # A small gap keeps the request-response protocol from tripping
                # over itself on slower USB stacks.
                time.sleep(0.05)
            results.append(check_datalog(dev))
    except Exception as e:
        print("Could not open the port: {}".format(e))
        return 1

    supported = [r for r in results if r[1] == "ok"]
    unsupported = [r for r in results if r[1] != "ok"]

    print("")
    print("SUPPORTED ({} capabilities):".format(len(supported)))
    print("-" * 70)
    for label, status, value, note in supported:
        print("  {}".format(label))
        print("      value: {}".format(value))
        if note:
            print("      note:  {}".format(note))
    print("")
    print("NOT AVAILABLE ON THIS DEVICE ({}):".format(len(unsupported)))
    print("-" * 70)
    for label, status, value, note in unsupported:
        print("  {}  ({})".format(label, status))

    print("")
    print("Reminder: there is no per-pulse timestamp command anywhere in this")
    print("list. The finest real time signal is polling the cumulative pulse")
    print("count. True per-pulse arrival timing needs a hardware pulse tap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
