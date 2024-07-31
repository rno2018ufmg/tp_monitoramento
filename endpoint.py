import json
from threading import Thread
import uuid
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums
import pymongo
import SensorEndpoint
import EndpointOutput
from math import sin

class Endpoint:
    def __init__(self):
        self.mqtt_client = paho.Client(callback_api_version = paho_enums.CallbackAPIVersion.VERSION2, userdata = {})
        self.mqtt_client.on_message = self.fill_client
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.subscribe("/sensor_monitors")
        self.received_data = False
        self.client_data: str = ""

    def fill_client(self, client : paho.Client, userdata: any, msg: paho.MQTTMessage) -> None:
        self.client_data = msg.payload.decode()
        self.received_data = True

    def get_message(self) -> str:
        return self.client_data
    
    def data_received(self) -> bool:
        return self.received_data

    def start(self) -> None:
        self.mqtt_client.loop_start()
    
    def stop(self) -> None:
        self.mqtt_client.loop_stop()

class EndpointEntities:
    
    def __init__(self, sensors_info: str):
        self.mongo_conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.sensors_info = json.loads(sensors_info)
        self.sensors: list[SensorEndpoint.SensorEndpoint] = []
        self.machine_id = str(self.sensors_info['machine_id'])
        self.logger = EndpointOutput.Logger()
        self.logger_t = Thread(target= self.logger.print_infos, args=())
        for i, iterator in enumerate(self.sensors_info["sensors"]):
            sensor_id = str(iterator['sensor_id'])
            self.sensors.insert(i, SensorEndpoint.SensorEndpoint(self.machine_id, sensor_id, self.logger, self.mongo_conn, float(iterator['min_value']), float(iterator['max_value']), float(iterator['warning_value'])))

        self.sensors_thread: list[Thread] = []
        for i, iterator in enumerate(self.sensors):
            self.sensors_thread.insert(i, Thread(target = self.sensors[i].operation_loop, args=()))

    def start_components(self):
        self.logger_t.start()
        for it in self.sensors_thread:
            it.start()

    def shutdown_all(self):
        exit(0)

endpoint: Endpoint = Endpoint()
endpoint.start()
data_received : bool = endpoint.data_received()
while(not data_received):
    data_received = endpoint.data_received()
endpoint.stop()

endpointEntities : EndpointEntities = EndpointEntities(endpoint.get_message())
endpointEntities.start_components()
