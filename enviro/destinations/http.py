from enviro.helpers import get_config
import urequests

def upload_reading(reading):
  url = get_config("custom_http_url")

  auth = None
  if get_config("custom_http_username"):
    auth = (get_config("custom_http_username"), get_config("custom_http_password"))

  try:
    # post reading data to http endpoint
    result = urequests.post(url, auth=auth, json=reading)
    result.close()
    return result.status_code in [200, 201, 202]
  except:
    pass      

  return False