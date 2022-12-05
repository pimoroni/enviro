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
    
    ##### SSL Change Start
    # two options, with or without SSL
    if config.mqtt_broker_ca_file:
      f = open("ca.crt")
      ssl_data = f.read()
      f.close()
      mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=60,
                               ssl=True, ssl_params={'cert': ssl_data})
    else:
    ##### SSL Change not set so do insecure connection
      mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=60)
    # Now continue with connection and upload
    mqtt_client.connect()
    mqtt_client.publish(f"enviro/{nickname}", ujson.dumps(reading), retain=True)
    mqtt_client.disconnect()
    return UPLOAD_SUCCESS
  except:
    logging.debug(f"  - an exception occurred when uploading")

  return UPLOAD_FAILED
