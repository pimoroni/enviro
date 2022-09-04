import urequests
import config
from phew import logging
import time

def upload_reading(reading):
  completed = False
  while not completed:
    status_code = send_reading(reading)
    if status_code == 429:
      time.sleep(30)
      completed = False
    else:
      completed = True
  return status_code == 200

def send_reading(reading):
  # create adafruit.io payload format
  payload = {
    "created_at": reading["timestamp"],
    "feeds": []
  }

  # add all the sensor readings
  nickname = config.nickname
  for key, value in reading["readings"].items():
    key = key.replace("_", "-")
    payload["feeds"].append({"key": f"{nickname}-{key}", "value": value})

  # send the payload
  username = config.adafruit_io_username
  headers = {'X-AIO-Key': config.adafruit_io_key, 'Content-Type': 'application/json'}
  url = f"http://io.adafruit.com/api/v2/{username}/groups/enviro/data"

  try:
    result = urequests.post(url, json=payload, headers=headers)
    result.close()
    logging.info(f"{result.status_code}: {result.reason}")
    return result.status_code
  except:
    pass
  
  return False
