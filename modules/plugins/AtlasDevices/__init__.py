# -*- coding: utf-8 -*-
print("LOADING ATLAS PLUGIN")

from modules import cbpi
from modules.core.hardware import SensorActive
from modules.core.props import Property

import string
import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver

import os
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
            print("Error 4: send_cmd failed.")
            return False


def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        dev_list.append(serial)
    return dev_list

def get_temp(dev_IN):    #COLLECT TEMP READING
    try:
        dev_IN.send_cmd("R")
        time.sleep(1) #WANT TO MAKE THIS SOCKETIOSLEEP
        lines = dev_IN.read_lines()
        for i in range(len(lines)):
            if lines[i][0] != '*':
                temp = lines[i]
                return temp
    except pylibftdi.FtdiError as e:
            print( "Error1, ", e)

def run_Temp(dev):  #PERFORMS ERROR CHECKING
    try:
        temp_raw = get_temp(dev)
        try:
            reading = float(temp_raw.strip())
            return reading
        except:
            print("Error5: could not convert temp_raw to float")
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "%s, Error converting to float: %s" % (formatted_time, temp_raw)
            log_error(msg)
    except pylibftdi.FtdiError as e:
        print("Error in run_temp, ", e)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = "%s, Error in get_temp with dev: %s" % (formatted_time, dev)
        log_error(msg)

def log_error(msg):
    error_log = "./logs/TempError.log"
    with open(error_log, "a") as file:
        file.write(msg)


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
                new_reading = run_Temp(self.dev)
                temp_dif = abs(new_reading - self.last_reading)
                if temp_dif > 5:                 
                    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    msg = "%s, New Reading: %s, Old Reading: %s \n" % (formatted_time, new_reading, self.last_reading)
                    log_error(msg)                  
                    print("Recorded Temp Error: New_Reading = %s, Old_reading = %s" % (new_reading, self.last_reading))
                else:
                    self.data_received(new_reading)
                    print("Sensor Reading from index %s = %s" % (self.index, new_reading))
                self.last_reading = new_reading
                self.sleep(2)
            except:
                print("Error3: could not run execute loop.")
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                msg = "%s, Error running temp loop\n" % formatted_time
                log_error(msg) 
                self.sleep(2)
                
    #@classmethod
    #def init_global(self):
        #pass


#@cbpi.initalizer()
#def init(cbpi):  
    #pass