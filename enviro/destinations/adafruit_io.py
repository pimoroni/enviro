from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED, UPLOAD_RATE_LIMITED
import urequests
import config

def log_destination():
  logging.info(f"> uploading cached readings to Adafruit.io: {config.adafruit_io_username}")

def upload_reading(reading):
  # create adafruit.io payload format
  payload = {
    "created_at": reading["timestamp"],
    "feeds": []
  }

  # add all the sensor readings
  nickname = config.nickname
  for key, value in reading["readings"].items():
    key = key.replace("_", "-")
    payload["feeds"].append({
      "key": f"{nickname}-{key}",
      "value": value
    })

  # send the payload
  username = config.adafruit_io_username
  headers = {'X-AIO-Key': config.adafruit_io_key, 'Content-Type': 'application/json'}
  url = f"http://io.adafruit.com/api/v2/{username}/groups/enviro/data"

  try:
    result = urequests.post(url, json=payload, headers=headers)
    result.close()
    if result.status_code == 429:
      return UPLOAD_RATE_LIMITED

    if result.status_code == 200:
      return UPLOAD_SUCCESS

    logging.debug(f"  - upload issue ({result.status_code} {result.reason})")
  except:
    logging.debug(f"  - an exception occurred when uploading")

  return UPLOAD_FAILED
