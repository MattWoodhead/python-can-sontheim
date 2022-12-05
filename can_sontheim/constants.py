"""
Ctypes constants module for the SIE / IFM CANfox interface

Copyright (C) 2022 Matt Woodhead
"""

from ctypes import (
    c_double,
    c_int,
    c_long,
    c_ulong,
    c_longlong,
    c_ulonglong,
    c_wchar_p,
    c_bool,
    c_ubyte,
    POINTER,
)
import sys

from can.ctypesutil import HANDLE
from .structures import (
    CANMsgStruct,
    CANMsgBuffer,
    CANStatusStruct,
    CANIDStatusStruct,
    CANCounterStruct,
    CANCounterStruct2,
    CANLevelHistStruct,
    CANBusLoadStruct,
    CANInstalledDevicesStruct,
)


IS_PYTHON_64BIT = sys.maxsize > 2**32


NTCAN_SUCCESS = 0
NTCAN_RX_TIMEOUT = -1
NTCAN_TX_TIMEOUT = -2
NTCAN_CONTR_BUSOFF = -3
NTCAN_NO_ID_ENABLED = -4
NTCAN_ID_ALREADY_ENABLED = -5
NTCAN_ID_NOT_ENABLED = -6
NTCAN_INVALID_PARAMETER = -7
NTCAN_INVALID_HANDLE = -8
NTCAN_TOO_MANY_HANDLES = -9
NTCAN_INIT_ERROR = -10
NTCAN_RESET_ERROR = -11
NTCAN_DRIVER_ERROR = -12
NTCAN_DLL_ALREADY_INIT = -13
NTCAN_CHANNEL_NOT_INITIALIZED = -14
NTCAN_TX_ERROR = -15
NTCAN_NO_SHAREDMEMORY = -16
NTCAN_HARDWARE_NOT_FOUND = -17
NTCAN_INVALID_NETNUMBER = -18
NTCAN_TOO_MANY_J2534_RANGES = -19
NTCAN_TOO_MANY_J2534_2_FILTERS = -20
NTCAN_DRIVER_NOT_INSTALLED = -21
NTCAN_NO_OWNER_RIGHTS = -22
NTCAN_FIRMWARE_TOO_OLD = -23
NTCAN_FIRMWARE_UNSUPPORTED = -24
NTCAN_FIRMWAREUPDATE_FAILED = -25
NTCAN_HARDWARE_NOT_SUPPORTED = -26
NTCAN_FILE_NOT_FOUND = -27
NTCAN_DEVICE_INFO_NOTAVAILABLE = -100
NTCAN_DEVICE_NOHW_ADDRESS = -101
NTCAN_NO_INTERRUPT_EVENT = -102
NTCAN_NO_INTERRUPT_EVENT_SET = -103
NTCAN_GET_MUTEX_FAILED = -104
NTCAN_NO_SHARED_MEMORY = -105
NTCAN_NET_NOT_AVAILABLE = -106
NTCAN_SETBAUDRATE_TIMEOUT = -107
NTCAN_EXE_ALREADYSTARTED = -108
NTCAN_NOTABLE_TOCREATE_SHAREDMEMORY = -109
NTCAN_HARDWARE_IN_USE = -110
NTCAN_API_NOT_RUNNING = -111
NTCAN_CHANNEL_CURR_NOT_AVAILABLE = -112
NTCAN_BUFFER_TOO_SMALL = -113
NTCAN_TOO_MANY_BRIDGE_FILTER = -114
NTCAN_HARDWARENOTACTIVE = -200
NTCAN_TOO_MANY_APPLICATIONS = -201
NTCAN_FLUSH_TIMEOUT = -202
NTCAN_NOSUCCESS = 0xFFFF0000

CANFOX_BITRATES = {
    1000000: 0,
    800000: 1,
    500000: 2,
    250000: 3,
    125000: 4,
    100000: 5,
    50000: 6,
    25000: 7,
}


# The functions defined in SIECA132.pdf
# Function name, response type, arguments tuple, error function (Optional)
_DLL_FUNCTIONS = [
    (
        "canOpen",
        c_long,
        (c_long, c_long, c_long, c_long, c_long, c_wchar_p, c_wchar_p, c_wchar_p, HANDLE),
    ),
    (
        "canOpenSH",
        c_long,
        (c_long, c_long, c_long, c_long, c_long, c_wchar_p, c_wchar_p, c_wchar_p, HANDLE),
    ),
    ("canClose", c_long, (HANDLE,)),
    ("canSetBaudrate", c_long, (HANDLE, c_long)),
    ("canSetBaudrateForce", c_long, (HANDLE, c_long)),
    ("canIsNetOwner", c_long, (HANDLE,)),
    ("canSetOwner", c_long, (c_long, HANDLE)),
    ("canGetOwner", c_long, (c_long, HANDLE)),
    ("canIdAdd", c_long, (HANDLE, c_long)),
    ("canIdAddArray", c_long, (HANDLE, POINTER(c_ubyte))),
    ("canIdDelete", c_long, (HANDLE, c_long)),
    ("canIdDeleteArray", c_long, (HANDLE,)),
    ("canIDStatus", c_long, (HANDLE, POINTER(CANIDStatusStruct))),
    ("canEnableAllIds", c_long, (HANDLE, c_bool)),
    ("canAreAllIdsEnabled", c_long, (HANDLE, POINTER(c_bool))),
    ("canSetFilterMode", c_long, (HANDLE, c_int)),
    ("canGetFilterMode", c_long, (HANDLE, c_int)),
    # "canSetFilterJ2534",
    ("canDeleteFilterJ2534", c_long, (HANDLE,)),
    # "canSetFilterJ2534_2",
    ("canDeleteFilterJ2534_2", c_long, (HANDLE,)),
    ("canSetBridgeFilter", c_long, (HANDLE, HANDLE, c_ulong, c_ulong, c_ulong)),
    # "canGetBridgeFilter",
    ("canClearBridgeFilter", c_long, (HANDLE, c_ulong, c_ulong, c_ulong, c_ulong)),
    #    ("canRead", c_long, (HANDLE, POINTER(CANMsgStruct), POINTER(c_long))),
    #    ("canRead", c_long, (HANDLE, POINTER(CANMsgBuffer(1)), POINTER(c_long))),
    #    ("canReadNoWait", c_long, (HANDLE, POINTER(CANMsgStruct), POINTER(c_long))),
    #    ("canReadNoWait", c_long, (HANDLE, POINTER(CANMsgBuffer(1)), POINTER(c_long))),
    ("canConfirmedTransmit", c_long, (HANDLE, POINTER(CANMsgStruct), POINTER(c_long))),
    ("canSend", c_long, (HANDLE, POINTER(CANMsgStruct), POINTER(c_long))),
    ("canWrite", c_long, (HANDLE, POINTER(CANMsgStruct), POINTER(c_long))),
    ("canFlush", c_long, (HANDLE, POINTER(c_long))),
    ("canStatus", c_long, (HANDLE, POINTER(CANStatusStruct))),
    # ("canGetDllInfo", c_long, (pointer, POINTER(c_void_p))),  # TODO: setup structure
    ("canGetCounter", c_long, (POINTER(CANCounterStruct),)),
    ("canGetCounterExtended", c_long, (HANDLE, POINTER(CANCounterStruct2))),
    ("canResetCounter", c_long, (HANDLE,)),
    ("canGetBusloadExtended", c_long, (HANDLE, POINTER(CANBusLoadStruct))),
    # "canGetTimeout",
    # "canSetTimeout",
    ("canBreakcanRead", c_long, (HANDLE,)),
    ("canClearBuffer", c_long, (HANDLE,)),
    ("canGetNumberOfConnectedDevices", c_long, (HANDLE,)),
    ("canGetDeviceList", c_long, (POINTER(CANInstalledDevicesStruct),)),
    ("canGetSyncTimer", c_long, (HANDLE, c_ulong, c_longlong)),
    ("canGetDeviceTimestampBase", c_long, (c_long, c_ulong)),
    ("canEnableHWExtendedId", c_long, (HANDLE, c_bool)),
    (
        "canGetCanLevel",
        c_long,
        (HANDLE, c_long, c_long, POINTER(c_double), POINTER(c_double)),
    ),
    ("canGetCanLevelHist", c_long, (HANDLE, c_bool, POINTER(CANLevelHistStruct))),
    ("canGetDiffTimeLastFrame", c_long, (HANDLE, POINTER(c_long))),
    ("canGetHWSerialNumber", c_long, (HANDLE, POINTER(c_ulong), POINTER(c_ulong))),
    ("canGetSystemTime", c_long, (POINTER(c_ulonglong), POINTER(c_ulonglong))),
    ("queryRunningVersion", c_long, (POINTER(c_ulong * 4),)),
    ("setApplicationFlags", c_long, (c_ulong,)),
    ("getApplicationFlags", c_long, (POINTER(c_ulong),)),
    ("canBlinkLED", c_long, (HANDLE, c_ulong, c_ulong, c_ulong)),
    ("canGetEepromAccess", c_long, (HANDLE, c_ulong, POINTER(c_ulong))),
    ("canReadEeprom", c_long, (HANDLE, c_long, c_long, POINTER(c_ubyte))),
    ("canWriteEeprom", c_long, (HANDLE, c_long, c_long, POINTER(c_ubyte))),
]
