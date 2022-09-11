from enviro.mqttsimple import MQTTClient
import ujson
import config

def upload_reading(reading):
  server = config.mqtt_broker_address
  username = config.mqtt_broker_username
  password = config.mqtt_broker_password
  nickname = reading["nickname"]

  try:
    # attempt to publish reading
    mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=10)
    mqtt_client.connect()
    mqtt_client.publish(f"enviro/{nickname}", ujson.dumps(reading), retain=True)
    mqtt_client.disconnect()
    return True
  except:
    pass

  return False
