# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 20:36:51 2022

sie_canfox_receive_multiple_example.py

python-can-sontheim
"""

from time import sleep
from pprint import pprint

import can
from can_sontheim import devices, _canlib


def main() -> None:

    print(f"System has events: {_canlib.HAS_EVENTS}")

    with can.Bus(interface="sontheim", channel=devices.CANfox.CAN1, bitrate=250000, echo=False) as bus:
        try:
            no_recv = True
            bus.clear_rx_buffer()
            while no_recv:
                msg = bus.recv(1)
                if msg is not None:
                    break
            print(msg)
            sleep(0.1)
            msgs = bus._recv_multiple(500)
            sleep(0.1)
            msgs = bus._recv_multiple(500)
            if (msgs is not None) or (msgs != []):
                pprint(msgs[0])
                print(len(msgs[0]))
        except KeyboardInterrupt:
            bus.shutdown()
        finally:
            bus.shutdown()


if __name__ == "__main__":

    main()
