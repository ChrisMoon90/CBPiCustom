import time
import os
from modules.app_config import socketio


class logAPI:
    def __init__(self):
        self.temps = {0: 0, 1: 0, 2: 0, 'Tilt': 0}
        self.filename = "./logs/Sensors.log"
        thread1 = socketio.start_background_task(target=self.save_to_file, sleep=5)

    def save_to_file(self, sleep):
        print("Starting Logging")
        socketio.sleep(10)
        print("Cont logging")

        while True: 
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "%s, %s, %s, %s, %s\n" % (formatted_time, self.temps[0], self.temps[1], self.temps[2], self.temps['Tilt'])
            print("Saving to File: %s" % self.temps)
            if os.path.exists(self.filename):
                with open(self.filename, "a") as f:
                    f.write(msg)
                socketio.sleep(sleep)
            else:
                print("Sensors.csv file does not exist. File will be created.")
                header = "Time, Temp 1, Temp 2, Temp 3, Tilt\n"
                with open(self.filename, 'a') as f:
                    f.write(header)
                    f.write(msg)
        print("Log Thread Terminated")


smartlog = logAPI()
