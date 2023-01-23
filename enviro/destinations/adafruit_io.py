from enviro import logging
from enviro.constants import *
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

    error_message = ""    
    try:
      error_message = result.json()['error']
    except (TypeError, KeyError):
      pass

    result.close()
    if result.status_code == 429:
      return UPLOAD_RATE_LIMITED

    if result.status_code == 200:
      return UPLOAD_SUCCESS

    if result.status_code == 422:
      if error_message.find("data created_at may not be in the future") == 0:
        return UPLOAD_LOST_SYNC

      logging.debug(f"  - upload issue '{error_message}' - You may have run out of feeds to upload data to")
      return UPLOAD_SKIP_FILE

    logging.debug(f"  - upload issue '{error_message}' ({result.status_code} - {result.reason.decode('utf-8')})")      

  except Exception as exc:
    import sys, io
    buf = io.StringIO()
    sys.print_exception(exc, buf)
    logging.debug(f"  - an exception occurred when uploading.", buf.getvalue())

  return UPLOAD_FAILED
