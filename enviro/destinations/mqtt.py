from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED
from enviro.mqttsimple import MQTTClient
import ujson
import config

def log_destination():
  logging.info(f"> uploading cached readings to MQTT broker: {config.mqtt_broker_address}")

def upload_reading(reading):
  server = config.mqtt_broker_address
  username = config.mqtt_broker_username
  password = config.mqtt_broker_password
  nickname = reading["nickname"]

  try:
    # attempt to publish reading
    mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=60)
    mqtt_client.connect()
    mqtt_client.publish(f"enviro/{nickname}", ujson.dumps(reading), retain=True)
    mqtt_client.disconnect()
    return UPLOAD_SUCCESS
  except:
    logging.debug(f"  - an exception occurred when uploading")

  return UPLOAD_FAILED
