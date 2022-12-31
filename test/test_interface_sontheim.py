"""
Test for Sontheim API Interface
"""

import ctypes
import unittest
from unittest import mock
from unittest.mock import Mock

import can
from can.bus import BusState
from can.exceptions import CanOperationError, CanInitializationError, CanTimeoutError
import can_sontheim.constants as const
from can_sontheim import SontheimBus, devices, IS_PYTHON_64BIT


skip_all_tests = IS_PYTHON_64BIT


class TestSontheimBus(unittest.TestCase):
    """unit tests for the sontheim bus"""

    @unittest.skipIf(skip_all_tests, reason="Currently requires 32 bit python interpreter only")
    def setUp(self) -> None:
        try:
            self.bus = can.Bus(interface="sontheim", channel=devices.CANfox.CAN1)
        except can.CanInterfaceNotImplementedError:
            raise unittest.SkipTest("Interface not available on this platform")

    @unittest.skipIf(skip_all_tests, reason="Currently requires 32 bit python interpreter only")
    def tearDown(self) -> None:
        if self.bus:
            self.bus.shutdown()
            self.bus = None

    @unittest.skipIf(skip_all_tests, reason="Currently requires 32 bit python interpreter only")
    def test_bus_creation(self) -> None:
        self.bus = can.Bus(bustype="sontheim")
        self.assertIsInstance(self.bus, SontheimBus)

    @unittest.skipIf(skip_all_tests, reason="Currently requires 32 bit python interpreter only")
    def test_bus_creation_state_error(self) -> None:
        with self.assertRaises(ValueError):
            can.Bus(bustype="sontheim", state=BusState.ERROR)

    @unittest.skipIf(skip_all_tests, reason="Currently requires 32 bit python interpreter only")
    def test_status(self) -> None:
        self.bus = can.Bus(bustype="sontheim")
        self.bus.status()


if __name__ == "__main__":
    unittest.main()
