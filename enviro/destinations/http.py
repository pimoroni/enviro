from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED
import requests
import config

def log_destination():
  logging.info(f"> uploading cached readings to url: {config.custom_http_url}")

def upload_reading(reading):
  url = config.custom_http_url

  auth = None
  if config.custom_http_username:
    auth = (config.custom_http_username, config.custom_http_password)

  try:
    # post reading data to http endpoint
    result = requests.post(url, auth=auth, json=reading)
    result.close()

    if result.status_code in [200, 201, 202]:
      return UPLOAD_SUCCESS

    logging.debug(f"  - upload issue ({result.status_code} {result.reason})")
  except Exception:  # noqa: BLE001
    logging.debug("  - an exception occurred when uploading")

  return UPLOAD_FAILED
