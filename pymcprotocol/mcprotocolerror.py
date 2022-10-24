# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:09:41 2022

@author: PC
"""

"""This file is collection of mcprotocol error.
"""

class MCProtocolError(Exception):
    """devicecode error. Device is not exsist.
    Attributes:
        plctype(str):       PLC type. "FX", "Q", "L" or "iQ"
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)
    """
    def __init__(self, errorcode):
        self.errorcode =  "0x" + format(errorcode, "x").rjust(4, "0").upper()

    def __str__(self):
        return "mc protocol error: error code {}".format(self.errorcode)

class UnsupportedComandError(Exception):
    """This command is not supported by the module you connected.  
    """
    def __init__(self, errorcode):
        self.errorcode = errorcode
        pass

    def __str__(self):
        return error_codes[self.errorcode]


error_codes = {0x50: " 0x50. Description: Codes for command/response type of subheader are not within the specifications (00 to 05H, 13 to 16H). Corrective Action: Check and correct command/ response type set by an external device. (The Ethernet adapter automatically adds command/ response type; the user does not need to set these.). • Check and correct the data length.",
               0x54: " 0x54. Description: When 'ASCII code communication' is selected in the [Communication data code settings] of operational setting parameters of GX Works2, ASCII code data that cannot be converted to binary code was received from an external device. Corrective Action: Check and correct the send data of the external device.",
               0x56: " 0x56. Description: Device designation from the external side is incorrect. Corrective Action: Correct the device designated.",
               0x57: " 0x57. Description: The number of points for a command designated by an external device exceeds the maximum number of processing points for each processing (number of processes that can be executed per communication). • Head device number to the designated points exceeds the maximum addresses (device number). • When performing batch read/write operations on C200 to C255, the number of device points was designated with an odd number. • Byte length of a command does not conform to the specifications. • When writing data, the set number of points for data to be written is different from the number of points specified. Corrective Action: Correct the designated points or device number. Check the data length of the command and adjust the data setting.",
               0x58: " 0x58. Description: Head device number of a command designated by an external device is set outside the allowable range. • A word device is designated in a command for bit devices. • The head number of bit devices is designated by a value other than a multiple of 16 in a command for word devices. Corrective Action: Designate the appropriate values within the range that are allowed for each processing. Correct the command or the designated device.",
               0x5B: " 0x5B. Description: The PLC and the Ethernet adapter cannot communicate. • The PLC cannot process requests from an external device. Corrective Action: Fix the faulty parts by referring to the abnormal codes appended to the end codes (3rd byte of the frame).",
               0x60: " 0x60. Description: Communication time between the Ethernet adapter and the PLC exceeded PLC monitoring timer value. Corrective Action: Increase the monitoring timer value."               
                }
    
def check_mcprotocol_error(status):
    """Check mc protocol command error.
    If errot exist(status != 0), raise Error.
    """
    if status == 0:
        return None
    elif status in error_codes.keys():
        raise UnsupportedComandError(error_codes[status])
    else:
        raise MCProtocolError(status)

