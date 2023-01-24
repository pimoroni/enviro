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
    if config.mqtt_broker_ca_file:
    # Using SSL
      f = open("ca.crt")
      ssl_data = f.read()
      f.close()
      mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=60,
                               ssl=True, ssl_params={'cert': ssl_data})
    else:
    # Not using SSL
      mqtt_client = MQTTClient(reading["uid"], server, user=username, password=password, keepalive=60)
    # Now continue with connection and upload
    mqtt_client.connect()
    mqtt_client.publish(f"enviro/{nickname}", ujson.dumps(reading), retain=True)
    mqtt_client.disconnect()
    return UPLOAD_SUCCESS

  # Try disconneting to see if it prevents hangs on this typew of errors recevied so far
  except (OSError, IndexError) as exc:
    try:
      import sys, io
      buf = io.StringIO()
      sys.print_exception(exc, buf)
      logging.debug(f"  - an exception occurred when uploading.", buf.getvalue())
      mqtt_client.disconnect()
    except Exception as exc:
      import sys, io
      buf = io.StringIO()
      sys.print_exception(exc, buf)
      logging.debug(f"  - an exception occurred when disconnecting mqtt client.", buf.getvalue())

  except Exception as exc:
    import sys, io
    buf = io.StringIO()
    sys.print_exception(exc, buf)
    logging.debug(f"  - an exception occurred when uploading.", buf.getvalue())

  return UPLOAD_FAILED
