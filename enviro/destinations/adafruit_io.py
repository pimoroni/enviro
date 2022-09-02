import urequests
import config

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
    payload["feeds"].append({"key": f"{nickname}-{key}", "value": value})

  # send the payload
  username = config.adafruit_io_username
  headers = {'X-AIO-Key': config.adafruit_io_key, 'Content-Type': 'application/json'}
  url = f"http://io.adafruit.com/api/v2/{username}/groups/enviro/data"

  try:
    result = urequests.post(url, json=payload, headers=headers)
    result.close()
    return result.status_code == 200
  except:
    pass
  
  return False