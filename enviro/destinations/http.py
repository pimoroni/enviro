import urequests
import config

def upload_reading(reading):
  url = config.custom_http_url

  auth = None
  if config.custom_http_username:
    auth = (config.custom_http_username, config.custom_http_password)

  try:
    # post reading data to http endpoint
    result = urequests.post(url, auth=auth, json=reading)
    result.close()
    return result.status_code in [200, 201, 202]
  except:
    pass      

  return False