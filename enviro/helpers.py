from enviro.constants import *
import machine, os, time

# miscellany
# ===========================================================================
def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}T{4:02d}:{5:02d}:{6:02d}Z".format(*dt)

def datetime_file_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}T{4:02d}_{5:02d}_{6:02d}Z".format(*dt)

def date_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d}".format(*dt)

def timestamp(dt):
  year = int(dt[0:4])
  month = int(dt[5:7])
  day = int(dt[8:10])
  hour = int(dt[11:13])
  minute = int(dt[14:16])
  second = int(dt[17:19])
  return time.mktime((year, month, day, hour, minute, second, 0, 0))

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

def copy_file(source, target):
  with open(source, "rb") as infile:
    with open(target, "wb") as outfile:
      while True:
        chunk = infile.read(1024)
        if not chunk:
          break
        outfile.write(chunk)

def write_config(config):
  lines = []
  with open("config.py", "r") as infile:
    lines = infile.read().split("\n")

  for i in range(0, len(lines)):
    line = lines[i]
    parts = line.split("=", 1)
    if len(parts) == 2:
      key = parts[0].strip()
      if hasattr(config, key):
        value = getattr(config, key)
        lines[i] = f"{key} = {repr(value)}"

  with open("config.py", "w") as outfile:
    outfile.write("\n".join(lines))
