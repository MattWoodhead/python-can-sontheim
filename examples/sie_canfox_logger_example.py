# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 20:36:51 2022

sie_canfox_logger_example.py

python-can-sontheim
"""

from datetime import datetime as dt

import can
from can_sontheim import devices


def main() -> None:

    bus = can.Bus(interface="sontheim", channel=devices.CANfox.CAN1, bitrate=250000, echo=False)

    start_time = dt.today().strftime("%Y-%m-%d_%H-%M-%S")

    print(f"Connected to {bus.__class__.__name__}: {bus.channel_info}")
    print(f"Can Logger (Started on {start_time})")

    logger = can.SizedRotatingLogger(base_filename=f"{start_time}_canfox_logger.asc", max_bytes=1024000)

    try:
        while True:
            msg = bus.recv(1)
            if msg is not None:
                logger(msg)
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()
        logger.stop()


if __name__ == "__main__":
    main()
