from enviro.constants import *
import machine, math, os, time, utime
from phew import logging

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

def uk_bst():
  # Return True if in UK BST - manually update bst_timestamps {} as needed
  dt = datetime_string()
  year = int(dt[0:4])
  ts = timestamp(dt)
  bst = False

  bst_timestamps = {
    2023: {"start": 1679792400, "end": 1698541200},
    2024: {"start": 1711846800, "end": 1729990800},
    2025: {"start": 1743296400, "end": 1761440400},
    2026: {"start": 1774746000, "end": 1792890000},
    2027: {"start": 1806195600, "end": 1824944400},
    2028: {"start": 1837645200, "end": 1856394000},
    2029: {"start": 1869094800, "end": 1887843600},
    2030: {"start": 1901149200, "end": 1919293200}
  }

  if year in bst_timestamps:
    if bst_timestamps[year]["start"] < ts and bst_timestamps[year]["end"] > ts:
      bst = True
  else:
    logging.warn(f"> Current year is not in BST lookup dictionary: {year}")
  return bst
  

# Return the day number of your timestamp string accommodating UTC offsets
def timestamp_day(dt, offset_hours):
  # Bounce via timestamp to properly calculate hours change
  time = timestamp(dt)
  time = time + (offset_hours * 3600)
  dt = utime.localtime(time)
  day = int(dt[2])
  return day

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

# temperature and humidity helpers
# ===========================================================================

# https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#what-is-and-how-to-calculate-absolute-humidity
def relative_to_absolute_humidity(relative_humidity, temperature_in_c):
  temperature_in_k = celcius_to_kelvin(temperature_in_c)
  actual_vapor_pressure = get_actual_vapor_pressure(relative_humidity, temperature_in_k)

  return actual_vapor_pressure / (WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k)

def absolute_to_relative_humidity(absolute_humidity, temperature_in_c):
  temperature_in_k = celcius_to_kelvin(temperature_in_c)
  saturation_vapor_pressure = get_saturation_vapor_pressure(temperature_in_k)

  return (WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k * absolute_humidity) / saturation_vapor_pressure * 100

def celcius_to_kelvin(temperature_in_c):
  return temperature_in_c + 273.15

# https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#actual-vapor-pressure
# http://cires1.colorado.edu/~voemel/vp.html
def get_actual_vapor_pressure(relative_humidity, temperature_in_k):
  return get_saturation_vapor_pressure(temperature_in_k) * (relative_humidity / 100)

def get_saturation_vapor_pressure(temperature_in_k):
  v = 1 - (temperature_in_k / CRITICAL_WATER_TEMPERATURE)

  # empirical constants
  a1 = -7.85951783
  a2 = 1.84408259
  a3 = -11.7866497
  a4 = 22.6807411
  a5 = -15.9618719
  a6 = 1.80122502

  return CRITICAL_WATER_PRESSURE * math.exp(
      CRITICAL_WATER_TEMPERATURE /
      temperature_in_k *
      (a1*v + a2*v**1.5 + a3*v**3 + a4*v**3.5 + a5*v**4 + a6*v**7.5)
  )
