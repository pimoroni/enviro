from enviro.helpers import get_config, uid
from enviro.mqttsimple import MQTTClient

def upload_reading(reading):
  server = get_config("mqtt_broker_address")
  username = get_config("mqtt_broker_username")
  password = get_config("mqtt_broker_password")
  nickname = get_config("nickname")

  try:
    # attempt to publish reading
    mqtt_client = MQTTClient(uid(), server, user=username, password=password)
    mqtt_client.connect()
    mqtt_client.publish(f"enviro/{nickname}", reading, retain=True)
    mqtt_client.disconnect()
    return True
  except:
    pass

  return False