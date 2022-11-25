# -*- coding: utf-8 -*-
from modules import cbpi
from modules.core.hardware import SensorActive
from modules.core.props import Property

from modules.SmartLogging import smartlog

# import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver

import time

class AtlasDevice(Device):

    def __init__(self, sn):
        Device.__init__(self, mode='t', device_id=sn)
        
    def DelDevice(self):
        Device.__del__(self)

    def read_line(self, size=0):
        lsl = len('\r')
        line_buffer = []
        while True:
            next_char = self.read(1)
            if next_char == '' or (size > 0 and len(line_buffer) > size):
                break
            line_buffer.append(next_char)
            if (len(line_buffer) >= lsl and
                    line_buffer[-lsl:] == list('\r')):
                break
        return ''.join(line_buffer)
    
    def read_lines(self):
        lines = []
        try:
            while True:
                line = self.read_line()
                if not line:
                    break
                    self.flush_input()
                lines.append(line)
            return lines       
        except FtdiError:
            print("Failed to read from the sensor.")
            return ''       

    def send_cmd(self, cmd):
        buf = cmd + "\r"        # add carriage return
        try:
            self.write(buf)
            return True
        except FtdiError:
            print("Error: send_cmd failed.")
            return False


def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        dev_list.append(serial)
    return dev_list

def log_error(msg):
    error_log = "./logs/TempError.log"
    with open(error_log, "a") as file:
        file.write(msg)

def send_to_logging(index, temp):
    index_val = int(str(index))
    smartlog.temps[index_val] = temp


@cbpi.sensor
class AtlasSensor(SensorActive):

    sensorSelect = Property.Select("Sensor Select", options=["0", "1", "2", "3"], description="Select available USB sensor")
    unitSelect = Property.Select("Unit Select", options=["Temp in F", "pH Value"], description="Select Unit")
    last_reading = 0
    
    # def init(self):
        #pass
    
    def get_unit(self):
        if self.unitSelect == "Temp in F":
            return " °F"
        elif self.unitSelect == "pH Value":
            return " pH"
        else:
            return "Select Data Type"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return:
        '''
        print("Atlas Sensor Stopped")
        pass
    
    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        self.index = self.sensorSelect
        self.devices = get_ftdi_device_list()
        self.dev = AtlasDevice(self.devices[int(self.index)])
        while self.is_running():
            try:
                self.dev.send_cmd("R")
                self.sleep(1.5) #MADE THIS SOCKETIOSLEEP & FIXED LATENCY ISSUE
                lines = self.dev.read_lines()
                for i in range(len(lines)):
                    if lines[i][0] != '*':
                        temp_raw = lines[i]
            except: #except pylibftdi.FtdiError as e:
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg = "%s, Error running get_temp @ dev: %s\n" % (formatted_time, self.dev)
                print(msg)
                log_error("%s\n" % (msg))
                temp_raw = "ERR"
                self.sleep(1.5)

            try:
                new_reading = float(temp_raw.strip())
                temp_dif = abs(new_reading - self.last_reading)
                if temp_dif > 10:                 
                    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    msg = "%s, New Reading: %s, Old Reading: %s, dev_index: %s" % (formatted_time, new_reading, self.last_reading, self.index)
                    print(msg)
                    log_error("%s\n" % (msg))                  
                else:
                    self.data_received(new_reading)
                    send_to_logging(self.index, new_reading)
                    print("Sensor Reading from index %s = %s" % (self.index, new_reading))
                self.last_reading = new_reading
            except:
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg = "%s, Error converting temp_raw to float: %s, dev_index: %s" % (formatted_time, temp_raw, self.index)
                print(msg)
                log_error("%s\n" % (msg))
            self.sleep(2)
                
    #@classmethod
    #def init_global(self):
        #pass


#@cbpi.initalizer()
#def init(cbpi):  
    #pass