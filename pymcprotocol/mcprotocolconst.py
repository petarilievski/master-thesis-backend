# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:07:51 2022

@author: PC
"""

"""This file defines mcprotocol constant.
"""
#PLC definetion
Q_SERIES    = "Q"
L_SERIES    = "L"
QnA_SERIES  = "QnA"
iQL_SERIES  = "iQ-L"
iQR_SERIES  = "iQ-R"
FX_SERIES   = "FX"

#communication type
COMMTYPE_BINARY = "binary"
COMMTYPE_ASCII  = "ascii"

class DeviceCodeError(Exception):
    """devicecode error. Device is not exsist.
    Attributes:
        plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)
    """
    def __init__(self, plctype, devicename):
        self.plctype = plctype
        self.devicename = devicename

    def __str__(self):
        error_txt = "devicename: {} is not support {} series PLC.\n"\
                    "If you enter hexadecimal device(X, Y, B, W, SB, SW, DX, DY, ZR) with only alphabet number\n"\
                    "(such as XFFF, device name is \"X\", device number is \"FFF\"),\n"\
                    "please insert 0 between device name and device number.\neg: XFFF → X0FFF".format(self.devicename, self.plctype)            
        return error_txt

class DeviceConstants:
    """This class defines mc protocol deveice constatnt.
    Attributes:
        D_DEVICE(int):  D devide code (0xA8)
    """
    #These device supports all series
    X_DEVICE = 0x5820
    Y_DEVICE = 0x5920
    M_DEVICE = 0x4D20
    L_DEVICE = 0x4D20
    S_DEVICE = 0x4D20
    F_DEVICE = 0x4260
    B_DEVICE = 0x4220
    TN_DEVICE = 0x544E
    TS_DEVICE = 0x5453
    TC_DEVICE = 0x5443
    CN_DEVICE = 0x434E
    CS_DEVICE = 0x4353
    CC_DEVICE = 0x4343
    D_DEVICE = 0x4420
    W_DEVICE = 0x5720
    R_DEVICE = 0x5220
    

    BIT_DEVICE  = "bit"
    WORD_DEVICE = "word"
    DWORD_DEVICE= "dword"

    
    def __init__(self):
        """Constructor
        """
        pass
    
    @staticmethod
    def get_binary_devicecode(plctype, devicename):
        """Static method that returns devicecode from device name.
        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")
        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → 0xA8)
            Base number:        Base number for each device name
        
        """
        
        if devicename == "X":
            return DeviceConstants.X_DEVICE, 16
        elif devicename == "Y":
            return DeviceConstants.Y_DEVICE, 16
        elif devicename == "M":
            return DeviceConstants.M_DEVICE, 10
        elif devicename == "L":
            return DeviceConstants.L_DEVICE, 10
        elif devicename == "S":
            return DeviceConstants.S_DEVICE, 10
        elif devicename == "F":
            return DeviceConstants.F_DEVICE, 10
        elif devicename == "B":
            return DeviceConstants.B_DEVICE, 16
        elif devicename == "D":
            return DeviceConstants.D_DEVICE, 10
        elif devicename == "W":
            return DeviceConstants.W_DEVICE, 16
        elif devicename == "TS":
            return DeviceConstants.TS_DEVICE, 10
        elif devicename == "TC":
            return DeviceConstants.TC_DEVICE, 10
        elif devicename == "TN":
            return DeviceConstants.TN_DEVICE, 10
        elif devicename == "CN":
            return DeviceConstants.CN_DEVICE, 10
        elif devicename == "CS":
            return DeviceConstants.CS_DEVICE, 10
        elif devicename == "CC":
            return DeviceConstants.CC_DEVICE, 10
        elif devicename == "R":
            return DeviceConstants.R_DEVICE, 10
        else:
            raise DeviceCodeError(plctype, devicename)

    @staticmethod
    def get_ascii_devicecode(plctype, devicename):
        """Static method that returns devicecode from device name.
        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")
        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → "D*")
            Base number:        Base number for each device name
        
        """
    
        padding = 2
        
        if devicename == "X":
            return devicename.ljust(padding, "*"), 16
        elif devicename == "Y":
            return devicename.ljust(padding, "*"), 16
        elif devicename == "M":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "S":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "L":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "F":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "V":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "B":
            return devicename.ljust(padding, "*"), 16
        elif devicename == "D":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "W":
            return devicename.ljust(padding, "*"), 16
        elif devicename == "TS":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "TC":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "TN":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "CS":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "CC":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "CN":
            return devicename.ljust(padding, "*"), 10
        elif devicename == "R":
            return devicename.ljust(padding, "*"), 10
        else:
            raise DeviceCodeError(plctype, devicename)

    @staticmethod
    def get_devicetype(plctype, devicename):
        """Static method that returns device type "bit" or "wrod" type.
        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")
        Returns:
            devicetyoe(str):    Device type. "bit" or "word"
        
        """
        
        if devicename == "X":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "Y":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "M":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "S":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "L":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "F":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "V":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "B":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "D":
            return DeviceConstants.WORD_DEVICE
        elif devicename == "W":
            return DeviceConstants.WORD_DEVICE
        elif devicename == "TS":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "TC":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "TN":
            return DeviceConstants.WORD_DEVICE
        elif devicename == "CS":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "CC":
            return DeviceConstants.BIT_DEVICE
        elif devicename == "CN":
            return DeviceConstants.WORD_DEVICE
        elif devicename == "R":
            return DeviceConstants.WORD_DEVICE
        else:
            raise DeviceCodeError(plctype, devicename)