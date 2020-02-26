# -*- coding: utf-8 -*-
from modules import cbpi
from modules.core.hardware import SensorActive
from modules.core.props import Property
import string
#import pylibftdi
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
        #print("buf = ", buf)
        try:
            self.write(buf)
            #print("SND =", self.write(buf))
            return True
        except FtdiError:
            print("Failed to send command to the sensor.")
            return False


def get_ftdi_device_list():
    dev_list = []    
    for device in Driver().list_devices():
        dev_info = device        
        vendor, product, serial = dev_info   # device must always be this triple
        dev_list.append(serial)
    return dev_list

def get_sensor(index):  #SELECT DEVICE   
    devices = get_ftdi_device_list()  
    while True:
        try:
            dev = AtlasDevice(devices[int(index)])
            return dev
        except pylibftdi.FtdiError as e:
            print( "Error0, ", e)
            time.sleep(2)

def get_temp(dev_IN):    #COLLECT TEMP READING
    while True:
        try:
            dev_IN.send_cmd("R")
            time.sleep(1)
            lines = dev_IN.read_lines()
            for i in range(len(lines)):
                if lines[i][0] != '*':
                    temp = lines[i]
                    dev_IN.__del__()
                    return temp
        except pylibftdi.FtdiError as e:
                print( "Error1, ", e)
                time.sleep(2)

def run_Temp(dev_active):  #PERFORMS ERROR CHECKING
    try:
        temp_long = get_temp(dev_active)
        #cbpi.app.logger.info("temp_long = %s" % temp_long)
        try:
            #temp = round(float(temp_long), 2)
            return temp_long
        except: #catch all exceptions
            print("Error Converting temp_long with float")
            time.sleep(1)
    except pylibftdi.FtdiError as e:
        print("Error1, ", e)
        time.sleep(2)


@cbpi.sensor
class AtlasSensor(SensorActive):

    sensorSelect = Property.Select("Sensor Select", options=["0", "1", "2", "3"], description="Select available USB sensor")
    unitSelect = Property.Select("Unit Select", options=["Temp in F", "pH Value"], description="Select Unit")
    
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
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        index = self.sensorSelect
        #print("Index Selected = ", index)              
        dev_active = get_sensor(index)
        #print("Active Device = ", dev_active)
        
        dev_active.send_cmd("C,0") # turn off continuous mode
        time.sleep(1)
        dev_active.flush()
        cbpi.app.logger.info("Device %s Flushed" % dev_active)
        time.sleep(1)
        
        dev_active.__del__()
        while self.is_running():
            dev_active = get_sensor(index)
            time.sleep(1)
            reading = run_Temp(dev_active)
            print("Sensor Reading = ", reading)
            
            self.data_received(reading)
            self.api.socketio.sleep(1)
            

@cbpi.initalizer()
def init(cbpi):  
    pass