import machine, os, time, network, usocket, struct
from enviro.constants import *

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)

def date_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}".format(*dt)

def mkdir_safe(path):
  try:
    os.mkdir(path)
  except OSError:
    pass # directory already exists, this is fine


from phew import logging

# put the wifi into access point mode with the specified ssid (and
# optional password)
def enter_access_point_mode(ssid, password = None):
  import rp2, network

  # start up network in access point mode
  rp2.country("GB")
  ap = network.WLAN(network.AP_IF)

  if ap.isconnected():
    ap.disconnect()

  ap.active(False)
  ap.config(essid=ssid)
  if password:
    ap.config(password=password)
  else:
    # disable password
    ap.config(security=0) 

  ap.active(True)

  return ap

def file_exists(filename):
  try:
    return (os.stat(filename)[0] & 0x4000) == 0
  except OSError:
    return False

def connect_to_wifi():
  wifi_ssid = get_config("wifi_ssid")
  wifi_password = get_config("wifi_password")

  logging.info("> connecting to wifi network:", wifi_ssid)

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(wifi_ssid, wifi_password)

  start = time.ticks_ms()
  while (time.ticks_ms() - start) < 30000:
    if wlan.status() < 0 or wlan.status() >= 3:
      break
    time.sleep(0.5)

  seconds_to_connect = int((time.ticks_ms() - start) / 1000)
  
  if wlan.status() != 3:
    logging.error("  - failed to connect")
    return False

  # a slow connection time will drain the battery faster and may
  # indicate a poor quality connection
  if seconds_to_connect > 5:
    logging.warn("  - took", seconds_to_connect, "seconds to connect to wifi")
  
  ip_address = wlan.ifconfig()[0]
  logging.info("  - ip address: ", ip_address)
  
  return True


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


def parse_template(response, template, **kwargs):
  import time

  start_time = time.ticks_ms()

  with open(template, "rb") as f:
    # read the whole template file, we could work on single lines but 
    # the performance is much worse - so long as our templates are
    # just a handful of kB it's ok to do this
    data = f.read()
    token_caret = 0

    while True:
      # find the next tag that needs evaluating
      start = data.find(b"{{", token_caret)
      end = data.find(b"}}", start)

      match = start != -1 and end != -1

      # no more magic to handle, just return what's left
      if not match:
        yield data[token_caret:]
        break

      expression = data[start + 2:end]

      # output the bit before the tag
      yield data[token_caret:start] 

      # merge locals with the supplied named arguments and
      # the response object
      params = {}
      params.update(locals())
      params.update(kwargs)
      params["response"] = response

      # parse the expression
      result = ""
      try:
        result = eval(expression, globals(), params)
      except:
        pass

      if type(result).__name__ == "generator":
        # if expression returned a generator then iterate it fully
        # and yield each result
        for include_line in result:
          yield include_line
      else:
        # yield the result of the expression
        if result:
          yield str(result)

      # discard the parsed bit
      token_caret = end + 2

  logging.info("    - parsed template:", template, " (", time.ticks_ms() - start_time, "ms)")


async def serve_template(response, template, **kwargs):
  logging.info("  - serve template: ", template)
  
  response.add_header("Content-Type", "text/html")
  await response._send_headers()

  for line in parse_template(response, template, **kwargs):
    await response.send(line)


def purge_logs():
  log_count = get_config("log_count", 10)
  logging.debug(f"> purging log files (max {log_count})")
  # get the creation time and filename of all log files
  log_files = {}
  for log in os.ilistdir("logs"):
    created = os.stat(f"logs/{log[0]}")[9]
    log_files[created] = log[0]
  # sort the creation times in descending order
  keys = sorted(log_files.keys(), reverse=True)
  # delete all log files after the max log count
  for key in keys[log_count:]:
    logging.debug(f"  - logs/{log_files[key]}")
    os.remove(f"logs/{log_files[key]}")