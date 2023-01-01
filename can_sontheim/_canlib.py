"""
Ctypes wrapper module for the SIE / IFM CANfox interface

Copyright (C) 2022 Matt Woodhead
"""
# standard library imports
from ctypes import c_int, c_long, c_ubyte, c_ulonglong, byref
import logging
import time
import platform
import sys

# imports from the python-can module
from can.message import Message
from can.bus import BusABC, BusState
from can.exceptions import CanOperationError, CanInitializationError, CanTimeoutError, CanInterfaceNotImplementedError
from can.ctypesutil import CLibrary, HANDLE

# from can.util import len2dlc, dlc2len

# local imports from the python-can-sontheim module
from .constants import (
    IS_PYTHON_64BIT,
    _DLL_FUNCTIONS,
    CANFOX_BITRATES,
    NTCAN_SUCCESS,
    NTCAN_RX_TIMEOUT,
    NTCAN_TX_TIMEOUT,
)
from .devices import CANfox, CANUSB, CANUSB_Legacy
from .structures import CANMsgStruct, CANMsgBuffer, CANInstalledDevicesStruct, read_struct_as_dict


try:
    # Try builtin Python 3 Windows API
    from _overlapped import CreateEvent
    from _winapi import WaitForSingleObject, WAIT_OBJECT_0, INFINITE

    HAS_EVENTS = True
except ImportError:
    try:
        # Try pywin32 package
        from win32event import CreateEvent
        from win32event import WaitForSingleObject, WAIT_OBJECT_0, INFINITE

        HAS_EVENTS = True
    except ImportError:
        # Use polling instead
        HAS_EVENTS = False


log = logging.getLogger("can.sontheim")  # Set up logging

_CANLIB = None
if sys.platform in ["win32", "cygwin"]:
    try:
        try:  # Check that python-can is being run on a 32 bit python interpreter
            assert not IS_PYTHON_64BIT
        except AssertionError as AE:
            raise CanInterfaceNotImplementedError(
                "The Sontheim API is currently only on 32 bit python interpreters"
            ) from AE
            # The SIE MT_API DLL is 32 bit only, so cannot be run from a 64 bit process
            # TODO: develop a 64 bit wrapper for the 32 bit API similar to msl-loadlib.
        _CANLIB = CLibrary("C:\\Program Files (x86)\\Sontheim\\MT_Api\\SIECA132.dll")
        for function, restype, argtypes in _DLL_FUNCTIONS:
            _CANLIB.map_symbol(function, restype, argtypes)
    except Exception as e:
        log.warning("Cannot load SIE MT_API for Sontheim: %s", e)

else:
    # Will not work on other systems, but have it importable anyway for
    # tests/sphinx
    log.warning(
        "Cannot load SIE MT_API for Sontheim does not work on %s platform, %s",
        sys.platform,
        platform.python_compiler(),
    )


def canGetSystemTime() -> int:
    """

    :raises SontheimCanOperationError:
        Raised if the Sontheim MT_API reports an error when querying the HW timestamp
    :return:
        The current system time in tenths of a millisecond (i.e divide by 10000 to get seconds)
    :rtype: int

    """

    pui64StartSysTime = c_ulonglong()
    pui64CurrSysTime = c_ulonglong()

    error_code = _CANLIB.canGetSystemTime(byref(pui64CurrSysTime), byref(pui64StartSysTime))

    if error_code != NTCAN_SUCCESS:
        raise CanOperationError("Error encountered in canGetSystemTime function call")
    return pui64CurrSysTime.value


class SontheimBus(BusABC):
    """
    A plugin for the python-can module, that allows the use of CAN interfaces that rely on the Sontheim Industrie
    Elektronik (SIE) MTAPI drivers. Currently Windows only and limited to 32 bit.
    """

    def __init__(
        self,
        channel=CANfox.CAN1,
        state=BusState.ACTIVE,
        bitrate=500000,
        *args,
        **kwargs,
    ):

        self.channel = channel
        self.channel_info = str(channel)
        self._canfox_bitrate = CANFOX_BITRATES.get(
            int(bitrate),
            CANFOX_BITRATES[500000],  # default to 500 kbit/s
        )
        self._Handle = HANDLE()
        self._bus_pc_start_time_s = None
        self._bus_hw_start_timestamp = None

        if state is BusState.ACTIVE or state is BusState.PASSIVE:
            self.state = state
        else:
            raise ValueError("BusState must be Active or Passive")

        if HAS_EVENTS:
            self._receive_event = CreateEvent(None, 0, 0, "R1")
            self._error_event = CreateEvent(None, 0, 0, "E1")

        super().__init__(channel=channel, state=state, bitrate=bitrate, *args, **kwargs)

        self._can_init(
            errors=kwargs.get(bool("errors"), True),
            echo=kwargs.get(bool("echo"), True),
            tx_timeout=kwargs.get("tx_timeout", -1),
            rx_timeout=kwargs.get("rx_timeout", -1),
        )

    def _can_init(self, errors=True, echo=False, tx_timeout=-1, rx_timeout=-1):

        # TODO: Check DLL status for DLL version - if it shows a value of zero, you need to unplug the adapter and plug it back in again to reset the driver

        error_code = _CANLIB.canOpen(
            c_long(int(self.channel)),
            c_long(errors),
            c_long(echo),
            c_long(tx_timeout),
            c_long(rx_timeout),
            "python-can",
            "R1",
            "E1",
            byref(self._Handle),
        )
        if error_code != NTCAN_SUCCESS:
            # raise CanInitializationError(
            #     "Error encountered whilst trying to open Sontheim bus interface, [Error Code: %s]" % error_code,
            # )
            raise CanInitializationError(
                f"Error encountered whilst trying to open Sontheim bus interface, [Error Code: {error_code}]",
            )

        error_code = _CANLIB.canSetBaudrate(self._Handle, c_int(self._canfox_bitrate))
        if error_code != NTCAN_SUCCESS:
            raise CanInitializationError(
                f"Error encountered whilst trying to set bus bitrate, [Error Code: {error_code}]",
            )
        error_code = _CANLIB.canSetFilterMode(self._Handle, c_int(4))
        if error_code != NTCAN_SUCCESS:
            raise CanInitializationError(
                f"Error encountered whilst trying to set bus filters, [Error Code: {error_code}]",
            )

        self._bus_pc_start_time_s = round(time.time(), 4)
        self._bus_hw_start_timestamp = canGetSystemTime() / 10000

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        # declare here, which is called by __init__()
        self._state = new_state  # pylint: disable=attribute-defined-outside-init

        if new_state is BusState.ACTIVE:
            pass  # TODO: change HW mode
            # self.m_objPCANBasic.SetValue(
            #     self.m_PcanHandle, PCAN_LISTEN_ONLY, PCAN_PARAMETER_OFF
            # )

        elif new_state is BusState.PASSIVE:
            pass  # TODO: change HW mode
            # When this mode is set, the CAN controller does not take part on active events
            # (eg. transmit CAN messages) but stays in a passive mode (CAN monitor),
            # in which it can analyse the traffic on the CAN bus used by a
            # PCAN channel. See also the Philips Data Sheet "SJA1000 Stand-alone CAN controller".
            # self.m_objPCANBasic.SetValue(
            #     self.m_PcanHandle, PCAN_LISTEN_ONLY, PCAN_PARAMETER_ON
            # )

    def shutdown(self):
        super().shutdown()
        _CANLIB.canClose(self._Handle)

    def _recv_internal(self, timeout):

        if HAS_EVENTS:
            # We will utilize events for the timeout handling
            timeout_ms = int(timeout * 1000) if timeout is not None else INFINITE
        elif timeout is not None:
            # Calculate max time
            end_time = time.perf_counter() + timeout

        log.debug("Trying to read a msg")

        msg_struct = CANMsgStruct()
        error_code = None
        while error_code is None:
            error_code = _CANLIB.canReadNoWait(self._Handle, byref(msg_struct), byref(c_long(1)))
            if error_code == NTCAN_RX_TIMEOUT:
                if HAS_EVENTS:
                    error_code = None
                    val = WaitForSingleObject(self._receive_event, timeout_ms)
                    if val != WAIT_OBJECT_0:
                        return None, False
                elif timeout is not None and time.perf_counter() >= end_time:
                    return None, False
                else:
                    error_code = None
                    time.sleep(0.001)
            elif error_code != NTCAN_SUCCESS:
                raise CanOperationError(
                    "Error encountered whilst trying to read bus, [Error Code: {error_code}]",
                )

        log.debug("Received a message")

        # remove bits 4 to 7 as these are reserved for other functionality
        dlc = int(msg_struct.by_len & 0x0F)

        # Use the starting timestamp
        timestamp = self._bus_pc_start_time_s + (int(msg_struct.ul_tstamp) / 10000) - self._bus_hw_start_timestamp

        frame_info = msg_struct.by_extended

        rx_msg = Message(
            timestamp=timestamp,
            arbitration_id=msg_struct.l_id,
            is_extended_id=frame_info & 2,
            is_remote_frame=msg_struct.by_remote & 1,
            is_error_frame=frame_info & 64,
            dlc=dlc,
            data=msg_struct.aby_data,
            is_fd=False,
            # bitrate_switch=bitrate_switch,
            # error_state_indicator=error_state_indicator,
        )

        return rx_msg, False

    def _recv_multiple(self, msg_buffer_length=20) -> list:

        log.debug("Trying to read multiple messages")

        msg_return_count = c_long(msg_buffer_length)
        msg_buffer = CANMsgBuffer(msg_buffer_length)
        error_code = None
        while error_code is None:
            error_code = _CANLIB.canReadNoWait(self._Handle, byref(msg_buffer), byref(msg_return_count))
            if error_code != NTCAN_SUCCESS:
                raise CanOperationError(
                    "Error encountered whilst trying to read bus, [Error Code: {error_code}]",
                )

        log.debug("Received %s message(s)", msg_return_count)

        message_list = []
        for i in range(msg_return_count.value):
            msg_struct = msg_buffer.msgs[i]
            # remove bits 4 to 7 as these are reserved for other functionality
            dlc = int(msg_struct.by_len & 0x0F)

            # Use the starting timestamp
            timestamp = self._bus_pc_start_time_s + (int(msg_struct.ul_tstamp) / 10000) - self._bus_hw_start_timestamp

            frame_info = msg_struct.by_extended

            rx_msg = Message(
                timestamp=timestamp,
                arbitration_id=msg_struct.l_id,
                is_extended_id=frame_info & 2,
                is_remote_frame=msg_struct.by_remote & 1,
                is_error_frame=frame_info & 64,
                dlc=dlc,
                data=msg_struct.aby_data,
                is_fd=False,
                # bitrate_switch=bitrate_switch,
                # error_state_indicator=error_state_indicator,
            )

            message_list.append(rx_msg)

        return message_list, False

    def send(self, msg, timeout=None):

        assert msg.dlc <= 8

        msg_struct = CANMsgStruct()

        # configure the message. ID, Data length, ID type, message type
        msg_struct.l_id = c_long(msg.arbitration_id)
        msg_struct.by_len = msg.dlc
        if msg.is_extended_id:
            msg_struct.by_extended = c_ubyte(2)  # 00000010
        else:
            msg_struct.by_extended = c_ubyte(1)  # 00000001
        if msg.is_remote_frame:
            msg_struct.by_remote = c_ubyte(1)  # 00000001
        else:
            msg_struct.by_remote = c_ubyte(0)  # 00000000

        # copy data
        for i in range(msg.dlc):
            msg_struct.aby_data[i] = msg.data[i]

        # error_code = _CANLIB.canConfirmedTransmit(self._Handle, byref(msg_struct), byref(c_long(1)))
        error_code = _CANLIB.canSend(self._Handle, byref(msg_struct), byref(c_long(1)))

        if error_code == NTCAN_TX_TIMEOUT:
            raise CanTimeoutError("Timeout whilst attempting to send message")
        if error_code != NTCAN_SUCCESS:
            raise CanOperationError(
                "Error encountered whilst trying to write to bus, [Error Code: {error_code}]",
            )

    def flush_tx_buffer(self):
        """
        This method flushes the transmit buffer to make sure all messages have been sent. Note: This is only available for use with the Sontheim CANUSB interface, and an exception will be raised if it is attempted with a different interface.

        :raises CanOperationError:
            Raised if the flush_tx_buffer method is attempted with an inteface other than the Sontheim CANUSB
        :raises CanTimeoutError:
            Raised if the operation completes because of a time out error
        :raises CanOperationError:
            Raised if a return code other than NTCAN_SUCCESS or NTCAN_TX_TIMEOUT is returned by the Sontheim API
        :return:
            None
        :rtype:
            None

        """
        try:
            assert self.channel in [
                CANUSB.CAN1,
                CANUSB.CAN2,
                CANUSB_Legacy.CAN1,
                CANUSB_Legacy.CAN2,
            ]
        except AssertionError as AE:
            raise CanOperationError(
                "The flush_tx_buffer method is only available on the sontheim CANUSB interface"
            ) from AE

        error_code = _CANLIB.canFlush(self._Handle, c_long(10000))  # ten second timeout

        if error_code == NTCAN_TX_TIMEOUT:
            raise CanTimeoutError("Timeout whilst attempting to flush TX buffer")
        if error_code != NTCAN_SUCCESS:
            raise CanOperationError(
                "Error encountered whilst trying to flush TX buffer, [Error Code: {error_code}]",
            )

    def canBlinkLED(self, blink_length_s=2):
        """

        :param blink_length_s: The length in seconds for how long the blinking is desired.
        :type blink_length_s: int

        """

        for i in range(int(blink_length_s / 0.25) + 1):
            _CANLIB.canBlinkLED(self._Handle, 1, i % 2, 5)
            time.sleep(0.25)

        error_code = _CANLIB.canBlinkLED(self._Handle, 0, i % 2, 5)
        if error_code != NTCAN_SUCCESS:
            raise CanOperationError(
                "Error encountered whilst trying to flash adpter LEDs, [Error Code: {error_code}]",
            )

    def clear_rx_buffer(self):
        """
        Clears the receive buffer in the attached CAN peripheral
        :raises CanOperationError: If an error was encountered trying to clear the buffer
        """
        error_code = _CANLIB.canClearBuffer(self._Handle)
        if error_code != NTCAN_SUCCESS:
            raise CanOperationError(
                "Error encountered whilst trying to clear the RX buffer, [Error Code: {error_code}]",
            )

    @staticmethod
    def _detect_available_configs():
        try:
            devices_struct = CANInstalledDevicesStruct()
            error_code = _CANLIB.canGetDeviceList(byref(devices_struct))
            if error_code == NTCAN_SUCCESS:
                _devices = read_struct_as_dict(devices_struct)
                if _devices:
                    return [{"interface": "sontheim", "channel": _devices["Net"]}]
            return []
        except AttributeError:
            # An AttributeError is raised when run on a 64 bit system even though the bus is not avalable
            # return an empty list to prevent issues with python-can detect_available_configs function
            return []

    def fileno(self) -> int:
        raise NotImplementedError("fileno is not implemented in the Sontheim CAN bus interfaces")

    # def __getattr__(self, item: str):
    #     return self.bus.__getattribute__(item)
