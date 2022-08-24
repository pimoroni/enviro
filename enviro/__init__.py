# set up and enable vsys hold as soon as possible so we don't go to sleep
import time, machine, sys, os, ujson#, btree

from machine import Pin
from enviro.constants import *
import enviro.board as board
import enviro.helpers as helpers
from enviro.helpers import file_exists, date_string, datetime_string
from phew import logging as logging

# sync pico sdk rtc object to correct time so that standard micropython date 
# and time methods return the correct value
t = board.rtc.datetime()
machine.RTC().datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0))


# will become our btree once the file is opened
_upload_cache = None


# jazz up that console! toot toot!
print("       ___            ___            ___          ___          ___            ___       ")
print("      /  /\          /__/\          /__/\        /  /\        /  /\          /  /\      ")
print("     /  /:/_         \  \:\         \  \:\      /  /:/       /  /::\        /  /::\     ")
print("    /  /:/ /\         \  \:\         \  \:\    /  /:/       /  /:/\:\      /  /:/\:\    ")
print("   /  /:/ /:/_    _____\__\:\    ___  \  \:\  /__/::\      /  /:/~/:/     /  /:/  \:\   ")
print("  /__/:/ /:/ /\  /__/::::::::\  /___\  \__\:\ \__\/\:\__  /__/:/ /:/___  /__/:/ \__\:\  ")
print("  \  \:\/:/ /:/  \  \:\^^^__\/  \  \:\ |  |:|    \  \:\/\ \  \:\/:::::/  \  \:\ /  /:/  ")
print("   \  \::/ /:/    \  \:\         \  \:\|  |:|     \__\::/  \  \::/^^^^    \  \:\  /:/   ")
print("    \  \:\/:/      \  \:\         \  \:\__|:|     /  /:/    \  \:\         \  \:\/:/    ")
print("     \  \::/        \  \:\         \  \::::/     /__/:/      \  \:\         \  \::/     ")
print("      \__\/          \__\/          `^^^^^`      \__\/        \__\/          \__\/      ")
print("")
print("       -  --  ---- ------=--==--===  i can has data?  ===--==--=------ ----  --  -      ")
print("")


def provision():
  # this import starts the provisioning process and control will never 
  # return from here
  import enviro.provisioning


# returns the reason we woke up
def wake_reason():
  reason = board.get_wake_reason()
  return board.wake_reason_name(reason)


# returns True if the board needs provisioning
def needs_provisioning():
  # if config fails to import (missing or corrupt) then we need to provision
  try:
    import config
    if not config.provisioned:
      return True
    return False
  except ImportError as e:
    logging.error("> error in config.py", e)
  return True


# returns True if we've used up 90% of the internal filesystem
def low_disk_space():
  try:
    return (os.statvfs(".")[3] / os.statvfs(".")[2]) < 0.1
  except:
    # os.statvfs doesn't exist on remote mounts but in that case we can
    # assume plenty of space
    pass
  return False


# returns True if the rtc clock has been set - PCF85063A defaults to year 2000
# so if current date much later then we know that the rtc has been synched
def clock_set():
  return board.rtc.datetime()[0] > 2020 # year greater than 2020? we're golden!


# connect to wifi and then attempt to fetch the current time from an ntp server
# once fetch set the onboard rtc and the pico's own rtc
def sync_clock_from_ntp():
  if not helpers.connect_to_wifi():
    return False
  t = helpers.update_rtc_from_ntp()
  if not t:
    logging.error("  - failed to fetch time from ntp server")
    return False
  # set the time on the rtc chip
  board.rtc.datetime((t[0], t[1], t[2], t[3], t[4], t[5], t[6]))
  # set the pico rtc time as well
  machine.RTC().datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0))      
  logging.info("  - rtc synched")      
  return True


# save the provided readings into a cache file for future uploading
def cache_upload(readings):
  # _upload_cache[helpers.datetime_string().encode("utf-8")] = json.dumps(readings).encode("utf-8")
  # _upload_cache.flush()
  # print(len(_upload_cache))
  uploads_filename = f"uploads/{helpers.datetime_string()}.json"
  with open(uploads_filename, "w") as f:
    f.write(ujson.dumps(readings))


# return the number of cached results waiting to be uploaded
def cached_upload_count():
  return len(os.listdir("uploads"))


# save the provided readings into a todays readings data file
def save_reading(readings):
  # open todays reading file and save readings
  readings_filename = f"readings/{helpers.date_string()}.txt"
  new_file = not helpers.file_exists(readings_filename)
  with open(readings_filename, "a") as f:
    if new_file:
      # new readings file so write out column headings first
      if qtstemma:
        f.write("time," + ",".join(sensors() + qtsensors()) + "\r\n")
      else: 
        f.write("time," + ",".join(sensors()) + "\r\n")

    # write sensor data
    row = [helpers.datetime_string()]
    if qtstemma is not None:
      row.extend(str(readings[key]) for key in (sensors() + qtsensors()))
    else:
      row.extend(str(readings[key]) for key in sensors())
    f.write(",".join(row) + "\r\n")


# returns true if the button is held for the number of seconds provided
def button_held_for(seconds):
  start = time.time()
  while board.button_pin.value():
    if time.time() - start > seconds:
      return True
    time.sleep(0.1)


# import board specific methods
model = board.model()
if model == "indoor":
  from enviro.boards.indoor import sensors, get_sensor_readings
if model == "grow":
  from enviro.boards.grow import sensors, get_sensor_readings
if model == "weather":
  from enviro.boards.weather import sensors, get_sensor_readings
if model == "urban":
  from enviro.boards.urban import sensors, get_sensor_readings

qtstemma = board.qtstemma()
if qtstemma == "scd41":
  from enviro.boards.scd41 import qtsensors, get_qtsensor_readings

destination = helpers.get_config("destination")
if destination == "http":
  from enviro.destinations.http import upload_readings
if destination == "mqtt":
  from enviro.destinations.mqtt import upload_readings
if destination == "adafruit_io":
  from enviro.destinations.adafruit_io import upload_readings

def startup():
  # truncate log to keep it to at most three blocks on disk)
  logging.truncate(8192)

  # write startup banner into log file
  logging.info("")
  logging.info("hey enviro, let's go!")
  logging.info(" - --=-=-===-=-=-- - ")
  logging.info("")
  logging.debug("> performing startup")

  # keep the power rail alive by holding VSYS_EN high
  logging.debug("  - hold vsys_en high")
  hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT, value=True)

  # log the wake reason
  logging.info("  - wake reason:", wake_reason())

  # also immediately turn on the LED to indicate that we're doing something
  logging.debug("  - turn on activity led")
  board.pulse_activity_led(0.5)

  # initialise the upload cache database
  #try:  
    # this is a bit clunky but we want to open the file in read/write mode
    # however that won't create the file if it doesn't exist, so we first
    # attempt to open it for read/write
  #  f = open("upload-cache.db", "r+b")
  #except OSError:
    # and if that fails we open it write (which would truncate an existing
    # file if it was there)
  #  f = open("upload-cache.db", "w+b")
  #_upload_cache = btree.open(f)

  # ensure we have a directory to store reading files
  helpers.mkdir_safe("readings")

  # ensure we have a directory to store reading files
  helpers.mkdir_safe("uploads")


def sleep(minutes = -1):
  logging.info("> going to sleep")

  # make sure the rtc flags are cleared before going back to sleep
  logging.debug("  - clearing rtc alarm flags")
  board.rtc.clear_timer_flag()
  board.rtc.clear_alarm_flag()

  # if wake time supplied then set rtc timer
  if minutes != -1:
    logging.info(f"  - setting timer to wake in {minutes} minutes")
    board.rtc.enable_timer_interrupt(True)
    board.rtc.set_timer(minutes, board.PCF85063A.TIMER_TICK_1_OVER_60HZ)  

  # disable the vsys hold, causing us to turn off
  logging.info("  - shutting down")
  board.hold_vsys_en_pin.init(Pin.IN)

  # if we're still awake it means power is coming from the USB port in which
  # case we can't (and don't need to) sleep.
  board.stop_activity_led()

  # we'll wait here until the rtc timer triggers and then reset the board
  logging.debug("  - on usb power (so can't shutdown) halt and reset instead")
  while not board.rtc.read_timer_flag():    
    time.sleep(0.1)

  logging.debug("  - hard reset")

  # reset the board
  board.reset()