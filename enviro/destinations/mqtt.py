from enviro.helpers import get_config, connect_to_wifi
from enviro import logging
import ujson, os
from enviro.mqttsimple import MQTTClient

def upload_readings():
  if not connect_to_wifi():
    logging.error(f"  - cannot upload readings, wifi connection failed")
    return False

  server = get_config("mqtt_broker_address")
  username = get_config("mqtt_broker_username")
  password = get_config("mqtt_broker_password")
  nickname = get_config("nickname")

  logging.info(f"> uploading cached readings to {server}")

  mqtt_client = MQTTClient(nickname, server, user=username, password=password, keepalive=60)
  mqtt_client.connect()

  for cache_file in os.ilistdir("uploads"):
    cache_file = cache_file[0]
    try:
      with open(f"uploads/{cache_file}", "r") as f:
        timestamp = cache_file.split(".")[0]
        data = ujson.load(f)

        payload = {
          "timestamp": timestamp,
          "device": nickname
        }
        for key, value in data.items():
          payload[key] = value

        topic = f"enviro/{nickname}"
        # by default the MQTT messages will be published with the retain flag
        # set, so that if a consumer is not subscribed, the most recent set
        # of readings can still be read by another subscriber later. Change
        # retain to False (or drop from the method call) below to change this
        mqtt_client.publish(topic, ujson.dumps(payload), retain=True)

        logging.info(f"  - uploaded {cache_file}")
        os.remove(f"uploads/{cache_file}")
    except OSError as e:
      logging.error(f"  - failed to upload '{cache_file}'")

  mqtt_client.disconnect()
