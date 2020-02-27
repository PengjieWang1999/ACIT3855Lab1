import connexion
import requests
import logging
import logging.config
from flask_cors import CORS, cross_origin
from connexion import NoContent
from pykafka import KafkaClient
import datetime
import json
import yaml

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

STORE_SERVICE_TEMPERATURE_URL = "http://localhost:8090/temperature"
STORE_SERVICE_HUMIDITY_URL = "http://localhost:8090/humidity"
HEADERS = {"content-type": "application/json"}

client = KafkaClient(hosts=app_config['datastore']['server'] + ':' + str(app_config['datastore']['port']))
topic = client.topics[app_config['datastore']['topic']]
producer = topic.get_sync_producer()


def report_humidity(humidityReading):

    msg = {"type": "hd",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": humidityReading}
    msg_str = json.dumps(msg)
    logger.debug("Humidity Events: " + msg_str)
    producer.produce(msg_str.encode('utf-8'))
    #response = requests.post(STORE_SERVICE_HUMIDITY_URL, json=humidityReading, headers=HEADERS)

    return NoContent, 201


def report_temperature(temperatureReading):
    msg = {"type": "tp",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": temperatureReading}
    msg_str = json.dumps(msg)
    logger.debug("Temperature Events: " + msg_str)
    producer.produce(msg_str.encode('utf-8'))
    #response = requests.post(STORE_SERVICE_TEMPERATURE_URL, json=temperatureReading, headers=HEADERS)
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml')

if __name__ == "__main__":
    app.run(port=8080)