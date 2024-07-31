from datetime import datetime, timezone
import json
import shutil
import time
import uuid
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums

class StorageMonitor:
    def __init__(self, machine_id: uuid.UUID, disk_path: str):
        self.machine_id: uuid.UUID = machine_id
        self.mqtt_client = paho.Client(callback_api_version = paho_enums.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.loop_start()
        self.disk_path : str = disk_path
        self.max_avaliable_storage : int = shutil.disk_usage(self.disk_path).total
        self.used_storage : float = 0.0
        self.delta_time = 100
        self.publish_endpoint = f"sensor/{self.machine_id}/disk_usage"
        self.is_running = True
        print(f"Publishing in: {self.publish_endpoint}")

    def get_storage_limit(self) -> int :    
        return self.max_avaliable_storage
    
    def get_storage_usage(self) -> int :
        return self.used_storage
    
    def get_disk_path(self) -> str:
        return self.disk_path

    def shutdown(self):
        self.mqtt_client.loop_stop()
        self.is_running = False

    def trace_sensor(self) -> None:
        while(self.is_running):
            start: float = time.time()
            self.used_storage: float = shutil.disk_usage(self.disk_path).used / self.max_avaliable_storage
            dt = datetime.now(timezone.utc)
            sensor = {
                "timestamp": f"{dt:%Y-%m-%d %H:%M:%S}.{dt.microsecond // 1000:03d}",
                "value": self.used_storage
            }
            string_result = json.dumps(sensor)
            self.mqtt_client.publish(self.publish_endpoint, payload=(string_result.encode()), qos=1)
            sleep_time = (self.delta_time/1000.0) + start
            sleep_time = sleep_time - time.time()
            if(sleep_time > 0.0):
                time.sleep(sleep_time)
        