"""
Ctypes Structures definitions module for the SIE / IFM CANfox interface

Copyright (C) 2022 Matt Woodhead
"""

from ctypes import (
    c_char,
    c_double,
    c_int,
    c_uint,
    c_short,
    c_ushort,
    c_long,
    c_ulong,
    c_longlong,
    c_ulonglong,
    c_byte,
    c_ubyte,
    c_void_p,
    c_bool,
    byref,
)
from ctypes import Structure


MAX_NUM_APIHANDLE = 4


def read_struct_as_dict(struct):
    result = {}
    # print struct
    def get_value(value):
        if (type(value) not in [int, float, bool]) and not bool(value):
            # it's a null pointer
            value = None
        elif hasattr(value, "_length_") and hasattr(value, "_type_"):
            # Probably an array
            # print value
            value = get_array(value)
        elif hasattr(value, "_fields_"):
            # Probably another struct
            value = read_struct_as_dict(value)
        return value

    def get_array(array):
        ar = []
        for value in array:
            value = get_value(value)
            ar.append(value)
        return ar

    for f in struct._fields_:
        field = f[0]
        value = getattr(struct, field)
        # if the type is not a primitive and it evaluates to False ...
        value = get_value(value)
        result[field] = value
    return result


class CANMsgStruct(Structure):
    _fields_ = [
        ("l_id", c_long),
        ("by_len", c_ubyte),
        ("by_msg_lost", c_ubyte),
        ("by_extended", c_ubyte),
        ("by_remote", c_ubyte),
        ("aby_data", c_ubyte * 8),
        ("ul_tstamp", c_ulong),
    ]  # CMSG


def CANMsgBuffer(length: int) -> Structure:
    """
    A Helper function to return a ctypes struct class object with a can message buffer
    of the desired length.
    :param length: The number of can messages to store in the struct
    :type length: int
    :return: The ctypes array of message structs
    :rtype: Structure
    """

    class _CANMsgBuffer(Structure):
        _fields_ = [("msgs", CANMsgStruct * length)]

    if length > 1:
        return _CANMsgBuffer()
    else:
        return _CANMsgBuffer  # return the class object for symbol mapping


class CANIDStatusStruct(Structure):
    _fields_ = [
        ("aby_ID", c_ubyte * 2048),
    ]  # T_ID_ARRAY


class CANStatusStruct(Structure):
    _fields_ = [
        ("w_hw_rev", c_ushort),
        ("w_fw_rev", c_ushort),
        ("w_drv_rev", c_ushort),
        ("w_dll_rev", c_ushort),
        ("ul_board_status", c_ulong),
        ("by_board_id", c_char),
        ("w_busoffctr", c_ushort),
        ("w_errorflag", c_ushort),
        ("w_errorframectr", c_ushort),
        ("w_netctr", c_ushort),
        ("w_baud", c_ushort),
        ("ui_epld_rev", c_uint),
    ]  # CAN_IF_STATUS


# class CANDLLStruct(Structure):
#     _fields_ = [
#         ("aui_TxCounter", c_uint * 2),
#         ("aui_TxHandleCounter", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_TxCounterRTR", c_uint * 2),
#         ("aui_TxHandleCounterRTR", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_TxThreadCounter", c_uint * 2),
#         ("aui_TxThreadCounterRTR", c_uint * 2),
#         ("aui_RxCounter", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_RxThreadCounter", c_uint * 2),
#         ("aui_RxBufferCounter", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_InterfaceCtr", c_uint * MAX_NUM_APIHANDLE),
#         ("appNames", STRINGARRAY),  # TODO - work out how to implement a stringaray in python
#         ("aui_ThreadStatus", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_ZugriffsCounterRead", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_ZugriffsCounterWrite", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_HandleNr", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_NetzZuordnung", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_NetzOwner", c_uint * 2),
#         ("aui_Reserve1601", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_Reserve1602", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_Reserve1603", c_uint * MAX_NUM_APIHANDLE),
#         ("aui_Reserve1604", c_uint * MAX_NUM_APIHANDLE),
#         ("ui_NetCount", c_uint),
#         ("ui_Reserve", c_uint),
#         ("aui_AnzahlEchoFrames", c_uint * 2),
#         ("ui_CloseZaehler", c_uint),
#         ("ui_OpenZaehler", c_uint),
#         ("ui_CloseFlag", c_uint),
#         ("ui_OpenedHandles", c_uint),
#     ]


class CANCounterStruct(Structure):
    _fields_ = [
        ("ul_timer", c_ulong),
        ("ul_rxframectr1", c_ulong),
        ("ul_txframectr1", c_ulong),
        ("ul_txremframectr1", c_ulong),
        ("ul_txdatabytectr1", c_ulong),
        ("ul_rxdatabytectr1", c_ulong),
        ("reserved0", c_ulong),
        ("ul_rxframectr2", c_ulong),
        ("l_txframectr2", c_ulong),
        ("ul_txremframectr2", c_ulong),
        ("ul_txdatabytectr2", c_ulong),
        ("ul_rxdatabytectr2", c_ulong),
        ("ul_CAN1ctrlflags", c_ulong),
        ("ul_CAN2ctrlflags", c_ulong),
        ("ul_errframectr1", c_ulong),
        ("ul_errframectr2", c_ulong),
    ]  # CTRDATA


class CANCounterStruct2(Structure):
    _fields_ = [
        ("ul_timer", c_ulong),
        ("ul_rxframectr1", c_ulong),
        ("ul_txframectr1", c_ulong),
        ("ul_txremframectr1", c_ulong),
        ("ul_txdatabytectr1", c_ulong),
        ("ul_rxdatabytectr1", c_ulong),
        ("reserved0", c_ulong),
        ("ul_rxframectr2", c_ulong),
        ("l_txframectr2", c_ulong),
        ("ul_txremframectr2", c_ulong),
        ("ul_txdatabytectr2", c_ulong),
        ("ul_rxdatabytectr2", c_ulong),
        ("ul_CAN1ctrlflags", c_ulong),
        ("ul_CAN2ctrlflags", c_ulong),
        ("ul_errctr1", c_ulong),
        ("ul_errctr2", c_ulong),
        ("ul_rxremframectr1", c_ulong),
        ("ul_erxframectr1", c_ulong),
        ("ul_etxframectr1", c_ulong),
        ("ul_etxremframectr1", c_ulong),
        ("ul_erxremframectr1", c_ulong),
        ("ul_rxremframectr2", c_ulong),
        ("ul_erxframectr2", c_ulong),
        ("ul_etxframectr2", c_ulong),
        ("ul_etxremframectr2", c_ulong),
        ("ul_erxremframectr2", c_ulong),
    ]  # CTRDATA2


# class CANTimeoutTypeStruct(Structure):  # TODO: Should be ENUM
#     _fields_ = [
#         ("aby_ID", c_ubyte * 2048),
#     ]  # T_ID_ARRAY


class CANInstalledDevicesStruct(Structure):
    _fields_ = [
        ("Net", c_int),
        ("Name", c_char * 20),
        ("ul_Status", c_ulong),
        ("ul_Features", c_ulong),
        ("Reserved", c_long * 18),
    ]  # T_DeviceList


# class CANTimeoutTypeStruct(Structure):  # TODO: Should be ENUM
#     _fields_ = [
#         ("canLevelDominant", c_uint),
#         ("canLevelRecessive", c_uint),
#     ]  # T_ID_ARRAY


class CANLevelHistStruct(Structure):
    _fields_ = [
        ("ulMeasureCountAll", c_ulong),
        ("arr_LevelLow", c_ulong * 50),
        ("arr_LevelHigh", c_ulong * 50),
        ("ulMeasureCountLowRez", c_ulong),
        ("dAvgLevelLowRez", c_double),
        ("dVariLevelLowRez", c_double),
        ("ulMeasureCountHighRez", c_ulong),
        ("dAvgLevelHighRez", c_double),
        ("dVariLevelHighRez", c_double),
        ("ulMeasureCountLowDom", c_ulong),
        ("dAvgLevelLowDom", c_double),
        ("dVariLevelLowDom", c_double),
        ("ulMeasureCountHighDom", c_ulong),
        ("dAvgLevelHighDom", c_double),
        ("dVariLevelHighDom", c_double),  # Variance of average level of dominant CAN HIGH
    ]  # CANLEVEL_HIST


# typedef enum
# {
# filterMode_standard = 0,
# filterMode_j2534 = 1,
# filterMode_extended = 2,
# filterMode_j2534_2 = 3,
# filterMode_nofilter = 4
# } T_FILTER_MODE;


# typedef enum
# {
# j2534Mode_excl = 0,
# j2534Mode_incl = 1
# } T_J2534_MODE;


class CANBusLoadStruct(Structure):
    _fields_ = [
        ("ul_intervall", c_ulong),
        ("ul_stdframectr", c_ulong),
        ("ul_stdframebytectr", c_ulong),
        ("ul_extframectr", c_ulong),
        ("ul_extframebytectr", c_ulong),
        ("ObjectTime", c_double),
        ("ul_load", c_ulong),
    ]  # BUSLOAD


class CANBridgeFilterStruct(Structure):
    _fields_ = [
        ("ulDestNet", c_ulong),
        ("ulPattern", c_ulong),
        ("ulMask", c_ulong),
        ("ulReserved", c_ulong),
    ]  # BRIDGE_FILTER
