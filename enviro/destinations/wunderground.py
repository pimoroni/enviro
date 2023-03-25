from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED
import urequests, time
import config
import enviro.helpers

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
  logging.info(f"> uploading cached readings to Weather Underground device: {config.wunderground_id}")

def upload_reading(reading):
  for key, value in reading["readings"].items():
    timestamp = reading["timestamp"]

    year = timestamp[0:4]
    month = timestamp[5:7]
    day = timestamp[8:10]
    hour = timestamp[11:13]
    minute = timestamp[14:16]
    second = timestamp[17:19]

    timestamp = year + "-" + month+ "-" + day + "+" + hour + "%3A" + minute + "%3A" + second

  url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?ID=" + config.wunderground_id + "&PASSWORD=" + config.wunderground_key + "&dateutc=" + timestamp

  logging.info(f"> upload url: {url}")

  return UPLOAD_SUCCESS