import machine, os, time, network, usocket, struct
from enviro.constants import *
import phew

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}T{4:02d}:{5:02d}:{6:02d}Z".format(*dt)

def date_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}".format(*dt)

def mkdir_safe(path):
  try:
    os.mkdir(path)
  except OSError:
    pass # directory already exists, this is fine


from phew import logging

def uid():
  return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(*machine.unique_id())

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

def connect_to_wifi():
  if phew.is_connected_to_wifi():
    logging.info(f"> already connected to wifi")
    return True

  wifi_ssid = get_config("wifi_ssid")
  wifi_password = get_config("wifi_password")

  logging.info(f"> connecting to wifi network '{wifi_ssid}'")
  ip = phew.connect_to_wifi(wifi_ssid, wifi_password, timeout_seconds=30)

  if not ip:
    logging.error(f"! failed to connect to wireless network {wifi_ssid}")
    return False

  logging.info("  - ip address: ", ip)

  return True


def copy_file(source, target):
  with open("enviro/config_template.py", "rb") as infile:
    with open("config.py", "wb") as outfile:
      while True:
        chunk = infile.read(1024)
        if not chunk:
          break
        outfile.write(chunk)


def set_values_in_file(filename, keys, values):
  if not isinstance(keys, list):
    values = {keys: values}
    keys = [keys]

  # rename current version of file while we write out new version
  os.rename(filename, filename + ".tmp")

  lines = []
  with open(filename + ".tmp", "r") as infile:
    for line in infile.read().split("\n"):
      parts = line.split("=")
      
      if len(parts) > 1:
        read_key = parts[0].strip()
        read_value = eval(parts[1].strip())
        if read_key in keys:
          # if this is the key we're modifying then change the line..
          value = values[read_key]
          try:
            value = int(value)
          except:
            pass
          line = read_key + " = " + repr(value)
      lines.append(line.strip())

  with open(filename, "w") as outfile:
    outfile.write("\r\n".join(lines))

  # clear up temporary file
  os.remove(filename + ".tmp")

def get_values_from_file(filename, key = None, default = None):
  # process each line in the config file looking for the matching key
  # or building a dictionary of the contents
  if not file_exists(filename):
    return default
    
  with open(filename, "r") as infile:
    result = {}  
    for line in infile.read().split("\n"):
      parts = line.split("=")
      if len(parts) > 1:
        read_key = parts[0].strip()
        read_value = eval(parts[1].strip())
        if key:
          if key == read_key:
            return read_value
        else:      
          result[read_key] = read_value
    return default if key else result


# config getter and setter
def get_config(key = None, default = None):
  if not file_exists("config.py"): # doesn't exist? copy from the template
    copy_file("enviro/config_template.py", "config.py")
  return get_values_from_file("config.py", key, default)

def set_config(key, value):  
  if not file_exists("config.py"): # doesn't exist? copy from the template
    copy_file("enviro/config_template.py", "config.py")
  set_values_in_file("config.py", key, value)


# state getter and setter
def get_state(key = None):
  return get_values_from_file("state.py", key)

def set_state(key, value):
  set_values_in_file("state.py", key, value)
