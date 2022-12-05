# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 20:36:51 2022

sie_canfox_tx_example.py

python-can-sontheim
"""

import can
from can import Message
from can_sontheim import devices
from threading import Timer
from time import ctime


DONE = False

with can.Bus(interface="sontheim", channel=devices.CANfox.CAN1, bitrate=250000, echo=False) as bus:

    def timeout():
        global DONE
        DONE = True

    msg = Message(
        arbitration_id=0xC0FFEF,
        is_extended_id=True,
        data=[0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF],
    )

    task = bus.send_periodic(msg, 1)
    t = Timer(10, timeout)
    t.start()
    print(f"TX started: {ctime()}")

    while not DONE:
        pass
    else:
        task.stop()
        print(f"TX Done: {ctime()}")
