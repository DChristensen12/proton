"""
Shared wrapper around the Rad Pro USB communications protocol.

Rad Pro is a request-response protocol, not a streaming one. You send an
ASCII command terminated with carriage-return-newline, and the device replies
with a line that starts with OK on success or ERROR on a bad request. Nothing
flows on its own, so everything here is built around send-command-wait-for-reply.

Reference: https://github.com/Gissio/radpro/blob/main/docs/comm.md
"""

import time
import serial
import serial.tools.list_ports


# These match the GC-01 running Rad Pro. They are fixed by the firmware.
BAUDRATE = 115200
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
LINE_TERMINATOR = b"\r\n"


class RadProError(Exception):
    """Raised when the device replies with ERROR or returns nothing."""
    pass


class RadProDevice:
    """
    A thin connection to a Rad Pro device over USB serial.

    Use it as a context manager so the port always gets closed:

        with RadProDevice("/dev/ttyACM0") as dev:
            print(dev.get_device_id())
    """

    def __init__(self, port, timeout=2.0):
        self.port = port
        self.timeout = timeout
        self._serial = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        self._serial = serial.Serial(
            port=self.port,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            timeout=self.timeout,
        )
        # Give the port a moment to settle after opening. Some USB stacks
        # reset the device on connect and we do not want to talk into a reboot.
        time.sleep(0.2)
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

    def close(self):
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def _send(self, command):
        """Write one command line to the device."""
        if self._serial is None or not self._serial.is_open:
            raise RadProError("Serial port is not open")
        payload = command.strip().encode("ascii") + LINE_TERMINATOR
        self._serial.write(payload)
        self._serial.flush()

    def _read_line(self):
        """Read one carriage-return-newline terminated reply."""
        raw = self._serial.readline()
        if not raw:
            raise RadProError("No reply from device, the read timed out")
        return raw.decode("ascii", errors="replace").strip()

    def command(self, command):
        """
        Send a command and return the payload after the OK token.

        Raises RadProError if the device replies ERROR or stays silent.
        """
        self._send(command)
        reply = self._read_line()
        if reply == "OK":
            return ""
        if reply.startswith("OK "):
            return reply[3:]
        if reply.startswith("ERROR"):
            raise RadProError("Device rejected command: " + command)
        # Some firmware versions occasionally echo a stray blank line first.
        # Try one more read before giving up.
        reply = self._read_line()
        if reply.startswith("OK "):
            return reply[3:]
        if reply == "OK":
            return ""
        raise RadProError("Unexpected reply to " + command + ": " + reply)

    # The named getters below cover every readable command in the protocol.
    # Anything marked supported-devices-only in the docs may return ERROR on
    # the GC-01, which raises RadProError that the caller can catch.

    def get_device_id(self):
        return self.command("GET deviceId")

    def get_battery_voltage(self):
        return float(self.command("GET deviceBatteryVoltage"))

    def get_device_time(self):
        return int(self.command("GET deviceTime"))

    def get_device_timezone(self):
        return float(self.command("GET deviceTimeZone"))

    def get_tube_time(self):
        return int(self.command("GET tubeTime"))

    def get_tube_pulse_count(self):
        return int(self.command("GET tubePulseCount"))

    def get_tube_rate(self):
        return float(self.command("GET tubeRate"))

    def get_tube_sensitivity(self):
        return float(self.command("GET tubeSensitivity"))

    def get_tube_dead_time(self):
        return float(self.command("GET tubeDeadTime"))

    def get_tube_dead_time_compensation(self):
        return float(self.command("GET tubeDeadTimeCompensation"))

    def get_tube_hv_frequency(self):
        return float(self.command("GET tubeHVFrequency"))

    def get_tube_hv_duty_cycle(self):
        return float(self.command("GET tubeHVDutyCycle"))

    def get_electric_field(self):
        return float(self.command("GET electricField"))

    def get_magnetic_field(self):
        return float(self.command("GET magneticField"))

    def get_random_data(self):
        return self.command("GET randomData")

    def get_datalog(self, start_time=0, end_time=4294967295, max_records=None):
        cmd = "GET datalog {} {}".format(start_time, end_time)
        if max_records is not None:
            cmd += " {}".format(max_records)
        return self.command(cmd)


def find_likely_ports():
    """
    List serial ports that look like they could be a Rad Pro device.

    On Linux the GC-01 usually shows up as /dev/ttyACM0. On Windows it is a
    COM port. We do not hard filter by vendor id here because we would rather
    show the user everything and let the deviceId check confirm it.
    """
    found = []
    for p in serial.tools.list_ports.comports():
        found.append({
            "device": p.device,
            "description": p.description or "",
            "vid": p.vid,
            "pid": p.pid,
            "serial_number": p.serial_number or "",
        })
    return found
