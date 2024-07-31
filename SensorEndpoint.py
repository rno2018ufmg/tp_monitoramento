import json
import uuid
import paho.mqtt.client as paho
import paho.mqtt.enums as paho_enums
import paho.mqtt.subscribe as subscribe
import pymongo
import EndpointOutput

class SensorEndpoint:
    def __init__(self, machine_id : uuid.UUID, topic: str, logger: EndpointOutput.Logger, mongo_conn: pymongo.MongoClient):
        self.machine_id = machine_id
        self.sensor_type = topic
        self.mydb = mongo_conn[str(machine_id)]
        self.mycol = self.mydb[topic]
        self.topic : str = f"sensor/{self.machine_id}/{self.sensor_type}"
        self.logger_callbacks = { "ram_usage": logger.push_ram, "disk_usage": logger.push_disk }
        self.active = True
        self.client_data: str = ""

    def fill_data(self, client : paho.Client, userdata: any, msg: paho.MQTTMessage) -> None:
        self.client_data = json.loads(msg.payload.decode())
        self.logger_callbacks[self.sensor_type](self.client_data["value"])
        self.mycol.insert_one(self.client_data)
        self.received_data = True

    def shutdown(self):
        self.active = False

    def get_message(self) -> str:
        return self.client_data
    
    def operation_loop(self):
        subscribe.callback(callback=self.fill_data, topics=self.topic, hostname="localhost", port=1883)
