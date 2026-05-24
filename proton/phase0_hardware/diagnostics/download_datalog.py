"""
Downloads the GC-01 on-device datalog and writes it to CSV.

Rad Pro logs time and cumulative pulse count pairs to internal flash, roughly
once a minute, even when the device is not connected. This pulls those records
out so you have a historical baseline without having to leave the laptop polling.
A pair of empty fields in the stream marks the start of a new logging session.

    python download_datalog.py --port /dev/ttyACM0 --out ../../../data/raw/datalog.csv
"""

import os
import sys
import csv
import argparse

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
))

from proton.common.radpro_serial import RadProDevice, RadProError, find_likely_ports


def resolve_port(requested):
    if requested:
        return requested
    ports = find_likely_ports()
    if not ports:
        return None
    return ports[0]["device"]


def parse_datalog(raw):
    """
    Turn the raw datalog reply into a list of rows.

    The reply is semicolon separated records, each comma separated. The first
    record is the header of field names. An empty record means a new session
    started, which we flag with a session index so sessions stay separable.
    """
    chunks = raw.split(";")
    rows = []
    header = None
    session = 0
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk == "":
            # Empty record marks a session boundary. Bump the session counter
            # so downstream code can tell logging restarts apart.
            session += 1
            continue
        fields = chunk.split(",")
        if header is None:
            header = fields
            continue
        if len(fields) == len(header):
            row = dict(zip(header, fields))
            row["session"] = session
            rows.append(row)
    return header, rows


def main():
    parser = argparse.ArgumentParser(description="Download GC-01 datalog to CSV")
    parser.add_argument("--port", help="Serial port. If omitted, uses first found.")
    parser.add_argument("--out", default="datalog.csv", help="Output CSV path")
    parser.add_argument("--start", type=int, default=0,
                        help="Unix start time, 0 for all earlier records")
    parser.add_argument("--end", type=int, default=4294967295,
                        help="Unix end time, max for all later records")
    args = parser.parse_args()

    port = resolve_port(args.port)
    if port is None:
        print("No serial ports found. Plug in the device with a data cable.")
        return 1

    try:
        with RadProDevice(port, timeout=10.0) as dev:
            # A longer timeout here because the full log can take a while to
            # come back over serial, and logging is paused during download.
            raw = dev.get_datalog(start_time=args.start, end_time=args.end)
    except RadProError as e:
        print("Could not read datalog: {}".format(e))
        return 1
    except Exception as e:
        print("Serial problem: {}".format(e))
        return 1

    header, rows = parse_datalog(raw)
    if not rows:
        print("No datalog records returned. The log may be empty.")
        print("Enable data logging in Settings and let it run, then try again.")
        return 0

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    fieldnames = list(header) + ["session"]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("Wrote {} records to {}".format(len(rows), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
