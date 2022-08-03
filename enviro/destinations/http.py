from enviro.helpers import get_config, connect_to_wifi
from enviro import logging
import urequests, ujson, os

def upload_readings():
  if not connect_to_wifi():
    logging.error(f"  - cannot upload readings, wifi connection failed")
    return False

  url = get_config("custom_http_url")
  logging.info(f"> uploading cached readings to {url}")

  auth = None
  if get_config("custom_http_username"):
    auth = (get_config("custom_http_username"), get_config("custom_http_password"))

  nickname = get_config("nickname")

  for cache_file in os.ilistdir("uploads"):
    cache_file = cache_file[0]
    try:
      with open(f"uploads/{cache_file}", "r") as f:
        timestamp = cache_file.split(".")[0]
        payload = {
          "nickname": nickname,
          "timestamp": timestamp,
          "data": ujson.load(f)
        }
        result = urequests.post(url, auth=auth, json=payload)
        if result.status_code != 200:
          logging.error(f"  - failed to upload '{cache_file}' ({result.status_code} {result.reason})", cache_file)
        else:
          logging.info(f"  - uploaded {cache_file}")
        os.remove(f"uploads/{cache_file}")

    except OSError as e:
      logging.error(f"  - failed to upload '{cache_file}'")
