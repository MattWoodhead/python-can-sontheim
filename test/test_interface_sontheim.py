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
import can.interfaces.sontheim.constants as const
from can.interfaces.sontheim import SontheimBus


class TestSontheimBus(unittest.TestCase):
    """unit tests for the sontheim bus"""

    def setUp(self) -> None:
        self.bus = None

    def tearDown(self) -> None:
        if self.bus:
            self.bus.shutdown()
            self.bus = None

    def test_bus_creation(self) -> None:
        self.bus = can.Bus(bustype="sontheim")
        self.assertIsInstance(self.bus, SontheimBus)

    def test_bus_creation_state_error(self) -> None:
        with self.assertRaises(ValueError):
            can.Bus(bustype="sontheim", state=BusState.ERROR)

    def test_status(self) -> None:
        self.bus = can.Bus(bustype="sontheim")
        self.bus.status()


if __name__ == "__main__":
    unittest.main()
