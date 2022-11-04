from enviro.constants import *

import machine, os

# miscellany
# ===========================================================================
def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}T{4:02d}:{5:02d}:{6:02d}Z".format(*dt)

def date_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}".format(*dt)

def uid():
  return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(*machine.unique_id())

# file management helpers
# ===========================================================================
def file_size(filename):
  try:
    return os.stat(filename)[6]
  except OSError:
    return None

def file_exists(filename):
  try:
    return (os.stat(filename)[0] & 0x4000) == 0
  except OSError:
    return False

def mkdir_safe(path):
  try:
    os.mkdir(path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
    pass # directory already exists, this is fine

# Keeping the below around for later comparisons with PHEW
"""
import machine, os, time, network, usocket, struct
from phew import logging
def update_rtc_from_ntp(max_attempts = 5):
  logging.info("> fetching date and time from ntp server")
  ntp_host = "pool.ntp.org"
  attempt = 1
  while attempt < max_attempts:
    try:
      logging.info("  - synching rtc attempt", attempt)
      query = bytearray(48)
      query[0] = 0x1b
      address = usocket.getaddrinfo(ntp_host, 123)[0][-1]
      socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
      socket.settimeout(30)
      socket.sendto(query, address)
      data = socket.recv(48)
      socket.close()
      local_epoch = 2208988800  # selected by Chris, by experiment. blame him. :-D
      timestamp = struct.unpack("!I", data[40:44])[0] - local_epoch
      t = time.gmtime(timestamp)
      return t      
    except Exception as e:
      logging.error(e)

    attempt += 1
  return False
"""
def copy_file(source, target):
  with open(source, "rb") as infile:
    with open(target, "wb") as outfile:
      while True:
        chunk = infile.read(1024)
        if not chunk:
          break
        outfile.write(chunk)
