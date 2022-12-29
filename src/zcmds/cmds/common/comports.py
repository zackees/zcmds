"""List serial ports."""

import serial.tools.list_ports  # type: ignore


def main() -> None:
    """List serial ports."""
    ports = serial.tools.list_ports.comports()

    for port, desc, hwid in sorted(ports):
        print("  {}: {} [{}]".format(port, desc, hwid))


if __name__ == "__main__":
    main()
