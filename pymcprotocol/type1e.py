# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:11:41 2022

@author: PC
"""

"""This file implements mcprotocol 1E type communication.
"""

import re
import time
import socket
import binascii
from pymcprotocol import mcprotocolerror
from pymcprotocol import mcprotocolconst as const

def isascii(text):
    """check text is all ascii character.
    Python 3.6 does not support str.isascii()
    """
    return all(ord(c) < 128 for c in text)

def twos_comp(val, mode="short"):
    """compute the 2's complement of int value val
    """
    if mode =="byte":
        bit = 8
    elif mode =="short":
        bit = 16
    elif mode== "long":
        bit = 32
    else:
        raise ValueError("cannnot calculate 2's complement")
    if (val & (1 << (bit - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bit)        # compute negative value
    return val 

def get_device_number(device):
    """Extract device number.
    Ex: "D1000" → "1000"
        "X0x1A" → "0x1A
    """
    device_num = re.search(r"\d.*", device)
    if device_num is None:
        raise ValueError("Invalid device number, {}".format(device))
    else:
        device_num_str = device_num.group(0)
    return device_num_str


class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"
    """
    def __init__(self):
        pass

    def __str__(self):
        return "communication type must be \"binary\" or \"ascii\""

class PLCTypeError(Exception):
    """PLC type error. PLC type must be"Q", "L", "QnA", "iQ-L", "iQ-R"
    """
    def __init__(self):
        pass

    def __str__(self):
        return "plctype must be \"Q\", \"L\", \"QnA\" \"iQ-L\" or \"iQ-R\""
    
class Type1E:
    """mcprotocol 1E communication class.
    Attributes:
        plctype(str):           connect PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", "FX"
        commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
        subheader(int):         Subheader for mc protocol
        network(int):           network No. of an access target. (0<= network <= 255)
        pc(int):                network module station No. of an access target. (0<= pc <= 255)
        timer(int):             time to raise Timeout error(/250msec). default=4(1sec)
                                If PLC elapsed this time, PLC returns Timeout answer.
                                Note: python socket timeout is always set timer+1sec. To recieve Timeout answer.
    """
    plctype         = const.FX_SERIES
    commtype        = const.COMMTYPE_BINARY
    subheader       = 0x00
    pc              = 0xFF #must be 0xFF. DO NOT CHANGE!
    timer           = 4 # MC protocol timeout. 250msec * 4 = 1 sec 
    soc_timeout     = 2 # 2 sec
    _is_connected   = False
    _SOCKBUFSIZE    = 4096
    _wordsize       = 2 #how many byte is required to describe word value 
                        #binary: 2, ascii:4.
    _debug          = False
    _monitor_words = 0
    _monitor_bits = 0
    
    def __init__(self, plctype ="FX"):
        """Constructor
        """
        self._set_plctype(plctype)
    
    def _set_debug(self, debug=False):
        """Turn on debug mode
        """
        self._debug = debug

    def connect(self, ip, port):
        """Connect to PLC
        Args:
            ip (str):       ip address(IPV4) to connect PLC
            port (int):     port number of connect PLC   
            timeout (float):  timeout second in communication
        """
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.soc_timeout)
        self._sock.connect((ip, port))
        self._is_connected = True

    def close(self):
        """Close connection
        """
        self._sock.close()
        self._is_connected = False

    def _send(self, send_data):
        """send mc protorocl data 
        Args: 
            send_data(bytes): mc protocol data
        
        """
        if self._is_connected:
            if self._debug:
                print(binascii.hexlify(send_data))
            self._sock.send(send_data)
        else:
            raise Exception("socket is not connected. Please use connect method")

    def _recv(self):
        """recieve mc protocol data
        Returns:
            recv_data
        """
        recv_data = self._sock.recv(self._SOCKBUFSIZE)
        return recv_data

    def _set_plctype(self, plctype):
        """Check PLC type. If plctype is vaild, set self.commtype.
        Args:
            plctype(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        """
        if plctype == "FX":
            self.plctype = const.FX_SERIES
        elif plctype == "L":
            self.plctype = const.L_SERIES
        elif plctype == "QnA":
            self.plctype = const.QnA_SERIES
        elif plctype == "iQ-L":
            self.plctype = const.iQL_SERIES
        elif plctype == "iQ-R":
            self.plctype = const.iQR_SERIES
        else:
            raise PLCTypeError()

    def _set_commtype(self, commtype):
        """Check communication type. If commtype is vaild, set self.commtype.
        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 
        """
        if commtype == "binary":
            self.commtype = const.COMMTYPE_BINARY
            self._wordsize = 2
        elif commtype == "ascii":
            self.commtype = const.COMMTYPE_ASCII
            self._wordsize = 4
        else:
            raise CommTypeError()

    def _get_answerdata_index(self):
        """Get answer data index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 2
        else:
            return 4

    def _get_answerstatus_index(self):
        """Get command status index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 1
        else:
            return 2
        
    def setaccessopt(self, commtype=None, 
                     pc=None, timer_sec=None):
        """Set mc protocol access option.
        Args:
            commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
            pc(int):                network module station No. of an access target. (0<= pc <= 255)
            timer_sec(int):         Time out to return Timeout Error from PLC. 
                                    MC protocol time is per 250msec, but for ease, setaccessopt requires per sec.
                                    Socket time out is set timer_sec + 1 sec.
        """
        if commtype:
            self._set_commtype(commtype)
        if pc:
            try:
                pc.to_bytes(1, "little")
                self.pc = pc
            except:
                raise ValueError("pc must be 0 <= pc <= 255") 
        if timer_sec:
            try:
                timer_250msec = 4 * timer_sec
                timer_250msec.to_bytes(2, "little")
                self.timer = timer_250msec
                self.soc_timeout = timer_sec + 1
                if self._is_connected:
                    self._sock.settimeout(self.soc_timeout)
            except:
                raise ValueError("timer_sec must be 0 <= timer_sec <= 16383, / sec") 
        return None
    
    def _make_senddata(self, requestdata):
        """Makes send mc protorocl data.
        Args:
            requestdata(bytes): mc protocol request data. 
                                data must be converted according to self.commtype
        Returns:
            mc_data(bytes):     send mc protorocl data
        """
        mc_data = bytes()
        # subheader is big endian
        mc_data += self._encode_value(self.pc, "byte")
        #add self.timer size
        #mc_data += self._encode_value(self._wordsize + len(requestdata), "short")
        mc_data += self._encode_value(self.timer, "short")
        mc_data = requestdata + mc_data
        return mc_data
    
    def _make_commanddata(self, command):
        """make mc protocol command data
        Args:
            command(int):       command code
        Returns:
            command_data(bytes):command data
        """
        command_data = bytes()
        
        command_data += self._encode_value(command, "byte")
        
        return command_data
    
    def _make_devicedata(self, device):
        """make mc protocol device data. (device code and device number)
        
        Args:
            device(str): device. (ex: "D1000", "Y1")
        Returns:
            device_data(bytes): device data
            
        """
        
        device_data = bytes()

        devicetype = re.search(r"\D+", device)
        if devicetype is None:
            raise ValueError("Invalid device ")
        else:
            devicetype = devicetype.group(0)      

        if self.commtype == const.COMMTYPE_BINARY:
            devicecode, devicebase = const.DeviceConstants.get_binary_devicecode(self.plctype, devicetype)
            devicenum = int(get_device_number(device), devicebase)
            if self.plctype is const.iQR_SERIES:
                device_data += devicenum.to_bytes(4, "little")
                device_data += devicecode.to_bytes(2, "little")
            else:
                device_data += devicenum.to_bytes(4, "little")
                device_data += devicecode.to_bytes(2, "little")
                
        else:
            devicecode, devicebase = const.DeviceConstants.get_ascii_devicecode(self.plctype, devicetype)
            devicenum = str(int(get_device_number(device), devicebase))
            if self.plctype is const.iQR_SERIES:
                device_data += devicecode.encode()
                device_data += devicenum.rjust(8, "0").upper().encode()
            else:
                device_data += devicecode.encode()
                device_data += devicenum.rjust(6, "0").upper().encode()
        return device_data

    def _encode_value(self, value, mode="short", isSigned=False):
        """encode mc protocol value data to byte.
        Args: 
            value(int):   readsize, write value, and so on.
            mode(str):    value type.
            isSigned(bool): convert as sigend value
        Returns:
            value_byte(bytes):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if mode == "byte":
                    value_byte = value.to_bytes(1, "little", signed=isSigned)
                elif mode == "short":
                    value_byte = value.to_bytes(2, "little", signed=isSigned)
                elif mode == "long":
                    value_byte = value.to_bytes(4, "little", signed=isSigned)
                else: 
                    raise ValueError("Please input value type")
            else:
                #check value range by to_bytes
                #convert to unsigned value
                if mode == "byte":
                    value.to_bytes(1, "little", signed=isSigned)
                    value = value & 0xff
                    value_byte = format(value, "x").rjust(2, "0").upper().encode()
                elif mode == "short":
                    value.to_bytes(2, "little", signed=isSigned)
                    value = value & 0xffff
                    value_byte = format(value, "x").rjust(4, "0").upper().encode()
                elif mode == "long":
                    value.to_bytes(4, "little", signed=isSigned)
                    value = value & 0xffffffff
                    value_byte = format(value, "x").rjust(8, "0").upper().encode()
                else: 
                    raise ValueError("Please input value type")
        except:
            raise ValueError("Exceeeded Device value range")
        return value_byte
    
    def _decode_value(self, byte, mode="short", isSigned=False):
        """decode byte to value
        Args: 
            byte(bytes):    readsize, write value, and so on.
            mode(str):      value type.
            isSigned(bool): convert as sigend value  
        Returns:
            value_data(int):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                value = int.from_bytes(byte, "little", signed = isSigned)
            else:
                value = int(byte.decode(), 16)
                if isSigned:
                    value = twos_comp(value, mode)
        except:
            raise ValueError("Could not decode byte to value")
        return value
    
    def _check_cmdanswer(self, recv_data):
        """check command answer. If answer status is not 0, raise error according to answer  
        """
        answerstatus_index = self._get_answerstatus_index()
        answerstatus = self._decode_value(recv_data[answerstatus_index:answerstatus_index+1], "short")
        mcprotocolerror.check_mcprotocol_error(answerstatus)
        return None
    
    def batchread_wordunits(self, headdevice, readsize):
        """batch read in word units.
        Args:
            headdevice(str):    Read head device. (ex: "D1000")
            readsize(int):      Number of read device points
        Returns:
            wordunits_values(list[int]):  word units value list
        """
        command = 0x01
        
        request_data = bytes()
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(readsize, mode="byte")
        request_data += self._encode_value(0, mode="byte")
       
        #send mc data
        self._send(request_data)
        #reciev mc data
        recv_data = self._recv()
        #print(recv_data)
        self._check_cmdanswer(recv_data)

        word_values = []
        data_index = self._get_answerdata_index()
        for _ in range(readsize):
            wordvalue = self._decode_value(recv_data[data_index:data_index+self._wordsize], mode="short", isSigned=True)
            word_values.append(wordvalue)
            data_index += self._wordsize
        return word_values

    def batchwrite_wordunits(self, headdevice, values):
        """batch write in word units.
        Args:
            headdevice(str):    Write head device. (ex: "D1000")
            values(list[int]):  Write values.
        """
        write_size = len(values)

        command = 0x03
        
        request_data = bytes()
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(write_size, mode="byte")
        request_data += self._encode_value(0, mode="byte")
        
        for value in values:
            request_data += self._encode_value(value, isSigned=True)
            

        #send mc data
        self._send(request_data)
        #print(request_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None
    
    def batchread_bitunits(self, headdevice, readsize):
        """batch read in bit units.
        Args:
            headdevice(str):    Read head device. (ex: "X1")
            size(int):          Number of read device points
        Returns:
            bitunits_values(list[int]):  bit units value(0 or 1) list
        """
        command = 0x00
        
        request_data = bytes()
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(readsize, mode="byte")
        request_data += self._encode_value(0, mode="byte")

        #send mc data
        self._send(request_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        #print(recv_data)

        bit_values = []
        if self.commtype == const.COMMTYPE_BINARY:
            for i in range(readsize):
                data_index = i//2 + self._get_answerdata_index()
                value = int.from_bytes(recv_data[data_index:data_index+1], "little")
                #if i//2==0, bit value is 4th bit
                if(i%2==0):
                    bitvalue = 1 if value & (1<<4) else 0
                else:
                    bitvalue = 1 if value & (1<<0) else 0
                bit_values.append(bitvalue)
        else:
            data_index = self._get_answerdata_index()
            byte_range = 1
            for i in range(readsize):
                bitvalue = int(recv_data[data_index:data_index+byte_range].decode())
                bit_values.append(bitvalue)
                data_index += byte_range
        return bit_values
    
    def batchwrite_bitunits(self, headdevice, values):
        """batch read in bit units.
        Args:
            headdevice(str):    Write head device. (ex: "X10")
            values(list[int]):  Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.
        """
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        command = 0x02
        
        request_data = bytes()
        
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(write_size, mode="byte")
        request_data += self._encode_value(0, mode="byte")
        
        
        if self.commtype == const.COMMTYPE_BINARY:
            #evary value is 0 or 1.
            #Even index's value turns on or off 4th bit, odd index's value turns on or off 0th bit.
            #First, create send data list. Length must be ceil of len(values).
            bit_data = [0 for _ in range((len(values) + 1)//2)]
            for index, value in enumerate(values):
                #calc which index data should be turns on.
                value_index = index//2
                #calc which bit should be turns on.
                bit_index = 4 if index%2 == 0 else 0
                #turns on or off value of 4th or 0th bit, depends on value
                bit_value = value << bit_index
                #Take or of send data
                bit_data[value_index] |= bit_value
            request_data += bytes(bit_data)
        else:
            for value in values:
                request_data += str(value).encode()
                    
        #send mc data
        self._send(request_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None

    
    def randomwrite_bitunits(self, bit_devices, values):
        """write bit units randomly.
        Args:
            bit_devices(list[str]):    Write bit devices. (ex: ["X10", "X20"])
            values(list[int]):         Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.
        """
        if len(bit_devices) != len(values):
            raise ValueError("bit_devices and values must be same length")
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        command = 0x04
        
        
        request_data = bytes()
        
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._encode_value(write_size, mode="byte")
        request_data += self._encode_value(0, mode="byte")
        
        for bit_device, value in zip(bit_devices, values):
            request_data += self._make_devicedata(bit_device)
            request_data += self._encode_value(value, mode="byte", isSigned=True)
                    
        #send mc data
        self._send(request_data)
        
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None
    
    def randomwrite_wordunits(self, word_devices, word_values):
        """write word units and dword units randomly.
        Args:
            word_devices(list[str]):    Write word devices. (ex: ["D1000", "D1020"])
            word_values(list[int]):     Values for each word devices. (ex: [100, 200])
        """
        if len(word_devices) != len(word_values):
            raise ValueError("word_devices and word_values must be same length")
            
        word_size = len(word_devices)
        
        command = 0x05
        
        request_data = bytes()
        
        request_data += self._make_commanddata(command)
        request_data = self._make_senddata(request_data)
        request_data += self._encode_value(word_size, mode="byte")
        request_data += self._encode_value(0, mode="byte")
        
        for word_device, word_value in zip(word_devices, word_values):
            request_data += self._make_devicedata(word_device)
            request_data += self._encode_value(word_value, mode="short", isSigned=True)

        #send mc data
        self._send(request_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None
    
    
    def monitorregistration_bitunits(self, bit_devices):
         """register which bit devices to monitor.
        Args:
            bit_devices(list[str]):    Register bit devices. (ex: ["X10", "X20"])
        """
        
         #THIS FUNCTION DOES NOT WORK CURRENTLY
        
         device_size = len(bit_devices)
         self._monitor_bits = device_size
        
         command = 0x06
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
         request_data += self._encode_value(device_size, mode="byte")
         request_data += self._encode_value(0, mode="byte")
        
         for bit_device in bit_devices:
             request_data += self._make_devicedata(bit_device)
        
         #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         self._check_cmdanswer(recv_data)
         return None
     
    def monitorregistration_wordunits(self, word_devices):
         """register which word devices to monitor.
        Args:
            word_devices(list[str]):    Register word devices. (ex: ["D100", "D200"])
        """
        
         #THIS FUNCTION DOES NOT WORK CURRENTLY
        
         device_size = len(word_devices)
         self._monitor_words = device_size
        
         command = 0x07
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
         request_data += self._encode_value(device_size, mode="byte")
         request_data += self._encode_value(0, mode="byte")
        
         for word_device in word_devices:
             request_data += self._make_devicedata(word_device)
             
        
         #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         self._check_cmdanswer(recv_data)
         return None
    
    def monitor_bitunits(self, readsize = 1024):
         """returns which monitored word devices.
         Returns:
            wordunits_values(list[int]):  word units value list
        """
         #THIS FUNCTION DOES NOT WORK CURRENTLY
        
         command = 0x08
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
        
           #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         self._check_cmdanswer(recv_data)
         #print(recv_data)
         
         bit_values = []
         if self.commtype == const.COMMTYPE_BINARY:
             for i in range(self._monitor_bits):
                 data_index = i//2 + self._get_answerdata_index()
                 value = int.from_bytes(recv_data[data_index:data_index+1], "little")
                 #if i//2==0, bit value is 4th bit
                 if(i%2==0):
                     bitvalue = 1 if value & (1<<4) else 0
                 else:
                     bitvalue = 1 if value & (1<<0) else 0
                 bit_values.append(bitvalue)
         else:
             data_index = self._get_answerdata_index()
             byte_range = 1
             for i in range(readsize):
                 bitvalue = int(recv_data[data_index:data_index+byte_range].decode())
                 bit_values.append(bitvalue)
                 data_index += byte_range
         return bit_values
     
    def monitor_wordunits(self):
         """returns which monitored word devices.
         Returns:
            wordunits_values(list[int]):  word units value list
        """
        
         #THIS FUNCTION DOES NOT WORK CURRENTLY
        
         command = 0x09
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
        
           #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         #print(recv_data)
         self._check_cmdanswer(recv_data)
         
         word_values = []
         data_index = self._get_answerdata_index()
         
         
         for _ in range(self._monitor_words):
             wordvalue = self._decode_value(recv_data[data_index:data_index+self._wordsize], mode="short", isSigned=True)
             word_values.append(wordvalue)
             data_index += self._wordsize
         return word_values


    def remote_run(self):
        
         command = 0x13
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
        
           #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         #print(recv_data)
         self._check_cmdanswer(recv_data)
         
    def remote_stop(self):
        
         command = 0x14
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
        
           #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         #print(recv_data)
         self._check_cmdanswer(recv_data)   
    
    def model_read(self):
        
         command = 0x15
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
        
           #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         #print(recv_data)
         self._check_cmdanswer(recv_data)
         
         data_index = self._get_answerdata_index()
         
         plc_type = recv_data[data_index:data_index+1]
         plc_type = bytes.hex(plc_type)
         
         return plc_type
     
    def loopback_test(self):
        
         #THIS FUNCTION DOES NOT WORK CURRENTLY
            
         command = 0x16
        
         request_data = bytes()
        
         request_data += self._make_commanddata(command)
         request_data = self._make_senddata(request_data)
         request_data += self._encode_value(2, mode="byte")
         request_data += self._encode_value(1, mode="byte")
         request_data += self._encode_value(2, mode="byte")
         
         print(request_data)
         
          #send mc data
         self._send(request_data)
         #reciev mc data
         recv_data = self._recv()
         #print(recv_data)
         self._check_cmdanswer(recv_data)
         
         values = []
         data_index = self._get_answerdata_index()
         for _ in range(3):
             wordvalue = self._decode_value(recv_data[data_index:data_index+1], mode="byte", isSigned=True)
             values.append(wordvalue)
             data_index += 1
             
         print(values)
         
         
         