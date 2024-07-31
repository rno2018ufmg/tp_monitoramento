import sys
import uuid
import machineid
import TemperatureMonitor
import VoltageMonitor
from threading import Thread
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums
import json
import time

class Monitor:

    def __init__(self):
        # Path 
        self.path = "D:/"
        self.machine_id = uuid.UUID(machineid.id())

        self.t = Thread(target=self.info_loop, args=(200,))
        self.reader_t = Thread(target=self.finish_thread, args=())

        self.ram_monitor : TemperatureMonitor.TemperatureMonitor = TemperatureMonitor.TemperatureMonitor(self.machine_id)
        self.storage_monitor : VoltageMonitor.VoltageMonitor = VoltageMonitor.VoltageMonitor(self.machine_id, self.path)
        self.ram_t = Thread(target=self.ram_monitor.trace_sensor, args=())
        self.storage_t = Thread(target=self.storage_monitor.trace_sensor, args=())

        self.running : bool = True

    def shutdown_all(self):
        
        self.running = False
        self.ram_monitor.shutdown()
        self.storage_monitor.shutdown()
        
        self.storage_t.join()
        self.ram_t.join()
        self.t.join()

    def join_reader(self):
        self.reader_t.join()

    def finish_thread(self):
        msg = input("Is time to finish [\"yes\"/\"no\"]? ")
        while(msg != "yes"):
            msg = input("Is time to finish [\"yes\"/\"no\"]? ")
        self.shutdown_all()

    def start_components(self):
        self.t.start()
        self.reader_t.start()
        self.ram_t.start()
        self.storage_t.start()

    def info_loop(self, delta_time: int):
        result = {
            "machine_id": f"{uuid.UUID(machineid.id())}",
            "sensors":[
                {
                    "sensor_id": "comp_temp",
                    "data_type": "float",
                    "data_interval": 100,
                    "min_value": 15.0,
                    "max_value": 65.0,
                    "warning_value": 52.0
                },
                {
                    "sensor_id": "comp_voltage",
                    "data_type": "float",
                    "data_interval": 100,
                    "min_value": 3.8,
                    "max_value": 5.2,
                    "warning_value": 4.8
                }
            ]
        }

        json_result = json.dumps(result)
        mqtt_client = paho.Client(callback_api_version = paho_enums.CallbackAPIVersion.VERSION2)
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        while(self.running):
            start : float = time.time()
            
            mqtt_client.publish("/sensor_monitors", payload=(json_result.encode()), qos=1)
            sleep_time = (delta_time/1000.0) + start
            sleep_time = sleep_time - time.time()
            if(sleep_time > 0.0):
                time.sleep(sleep_time)
        mqtt_client.loop_stop()
    

monitor = Monitor()
monitor.start_components()
monitor.join_reader()
