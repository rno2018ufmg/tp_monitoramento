import json
import random
import time
import uuid
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums
from datetime import datetime, timezone
from collections import deque

class TemperatureMonitor:
    def __init__(self, machine_id: uuid.UUID):
        self.machine_id: uuid.UUID = machine_id
        self.mqtt_client = paho.Client(callback_api_version = paho_enums.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.loop_start()
        self.filled_values = 0
        self.average_window: deque[float] = deque(maxlen=8)
        self.delta_time = 100
        self.publish_endpoint = f"sensor/{self.machine_id}/comp_temp"
        self.is_running = True
        print(f"Publishing in: {self.publish_endpoint}")

    def get_ram_limit(self) -> int :    
        return self.max_avaliable_ram
    
    def get_ram_usage(self) -> int :
        return self.used_ram
    
    def shutdown(self):
        self.mqtt_client.loop_stop()
        self.is_running = False

    def slide_average(self, value: float) -> float:
        if(self.filled_values < 8):
            self.filled_values += 1
        self.average_window.append(value)
        value = 0.0
        for i in self.average_window:
            value += i
        return value/(self.filled_values*1.0)

    def trace_sensor(self) -> None:
        while(self.is_running):
            start : float = time.time()
            dt = datetime.now(timezone.utc)
            sensor = {
                "timestamp": f"{dt:%Y-%m-%d %H:%M:%S}.{dt.microsecond // 1000:03d}",
                "value": self.slide_average(random.uniform(15.0, 65.0))
            }
            string_result = json.dumps(sensor)
            self.mqtt_client.publish(self.publish_endpoint, payload=(string_result.encode()), qos=1)
            sleep_time = (self.delta_time/1000.0) + start
            sleep_time = sleep_time - time.time()
            if(sleep_time > 0.0):
                time.sleep(sleep_time)
