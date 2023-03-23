from enviro import logging
from enviro.constants import UPLOAD_SUCCESS, UPLOAD_FAILED
import urequests, time
import config
from helpers import celcius_to_fahrenheit, hpa_to_inches, metres_per_second_to_miles_per_hour, mm_to_inches

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

