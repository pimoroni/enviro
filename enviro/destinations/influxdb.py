from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED
import urequests, time
import config

def url_encode(t):
  result = ""
  for c in t:
    # no encoding needed for character
    if c.isalpha() or c.isdigit() or c in ["-", "_", "."]:
      result += c
    elif c == " ":
      result += "+"
    else:
      result += f"%{ord(c):02X}"
  return result

def log_destination():
  logging.info(f"> uploading cached readings to Influxdb bucket: {config.influxdb_bucket}")

def upload_reading(reading):  
  bucket = config.influxdb_bucket

  payload = ""
  for key, value in reading["readings"].items():
    if payload != "":
      payload += "\n"
    timestamp = reading["timestamp"]

    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hour = int(timestamp[11:13])
    minute = int(timestamp[14:16])
    second = int(timestamp[17:19])
    timestamp = time.mktime((year, month, day, hour, minute, second, 0, 0))

    nickname = reading["nickname"]
    payload += f"{key},device={nickname} value={value} {timestamp}"

  influxdb_token = config.influxdb_token
  headers = {
    "Authorization": f"Token {influxdb_token}"
  }

  url = config.influxdb_url
  org = config.influxdb_org
  url += f"/api/v2/write?precision=s&org={url_encode(org)}&bucket={url_encode(bucket)}"
 
  try:
    # post reading data to http endpoint
    result = urequests.post(url, headers=headers, data=payload)
    result.close()
    
    if result.status_code == 204:  # why 204? we'll never know...
      return UPLOAD_SUCCESS

    logging.debug(f"  - upload issue ({result.status_code} {result.reason})")
  except:
    logging.debug(f"  - an exception occurred when uploading")

  return UPLOAD_FAILED