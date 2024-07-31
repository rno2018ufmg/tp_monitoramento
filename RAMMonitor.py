import json
import time
import psutil
import uuid
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums
from datetime import datetime, timezone



class RAMMonitor:
    def __init__(self, machine_id: uuid.UUID):
        self.machine_id: uuid.UUID = machine_id
        self.mqtt_client = paho.Client(callback_api_version = paho_enums.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.loop_start()
        self.max_avaliable_ram : int = psutil.virtual_memory().total
        self.used_ram : int = 0
        self.delta_time = 100
        self.publish_endpoint = f"sensor/{self.machine_id}/ram_usage"
        self.is_running = True
        print(f"Publishing in: {self.publish_endpoint}")

    def get_ram_limit(self) -> int :    
        return self.max_avaliable_ram
    
    def get_ram_usage(self) -> int :
        return self.used_ram
    
    def shutdown(self):
        self.mqtt_client.loop_stop()
        self.is_running = False

    def trace_sensor(self) -> None:
        while(self.is_running):
            start : float = time.time()
            memory_avaliable = psutil.virtual_memory().available
            self.used_ram = self.max_avaliable_ram - memory_avaliable
            dt = datetime.now(timezone.utc)
            sensor = {
                "timestamp": f"{dt:%Y-%m-%d %H:%M:%S}.{dt.microsecond // 1000:03d}",
                "value": (self.used_ram / self.max_avaliable_ram)
            }
            string_result = json.dumps(sensor)
            self.mqtt_client.publish(self.publish_endpoint, payload=(string_result.encode()), qos=1)
            sleep_time = (self.delta_time/1000.0) + start
            sleep_time = sleep_time - time.time()
            if(sleep_time > 0.0):
                time.sleep(sleep_time)
        
