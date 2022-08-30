# set up and enable vsys hold as soon as possible so we don't go to sleep
import math, time, machine, sys, os, ujson, rp2
from machine import Pin, PWM, Timer
from pimoroni_i2c import PimoroniI2C
from pcf85063a import PCF85063A
from enviro.constants import *
import enviro.helpers as helpers
from enviro.helpers import file_exists, date_string, datetime_string
from phew import logging, ntp

rp2.country("GB")

# set up the button, external trigger, and rtc alarm pins
button_pin = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
rtc_alarm_pin = Pin(RTC_ALARM_PIN, Pin.IN, Pin.PULL_DOWN)
external_trigger_pin = Pin(EXTERNAL_INTERRUPT_PIN, Pin.IN, Pin.PULL_DOWN)

hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT, value=True)

# setup the i2c bus
i2c = PimoroniI2C(I2C_SDA_PIN, I2C_SCL_PIN, 100000)

# set up the activity led
activity_led_pwm = PWM(Pin(ACTIVITY_LED_PIN))
activity_led_pwm.freq(1000)
activity_led_pwm.duty_u16(0)

activity_led_timer = Timer(-1)
activity_led_pulse_speed_hz = 1

# intialise the pcf85063a real time clock chip
rtc = PCF85063A(i2c)

# ensure rtc clock is running - this should be true anyway?
i2c.writeto_mem(0x51, 0x00, b'\x00')

# sync pico sdk rtc object to correct time so that standard micropython date 
# and time methods return the correct value
t = rtc.datetime()
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
  reason = get_wake_reason()
  return wake_reason_name(reason)


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
  return rtc.datetime()[0] > 2020 # year greater than 2020? we're golden!


# connect to wifi and then attempt to fetch the current time from an ntp server
# once fetch set the onboard rtc and the pico's own rtc
def sync_clock_from_ntp():
  if not helpers.connect_to_wifi():
    return False

  timestamp = ntp.fetch()
  if not timestamp:
    logging.error("  - failed to fetch time from ntp server")
    return False

  # set the time on the rtc chip
  rtc.datetime(timestamp)
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
      f.write("time," + ",".join(sensors()) + "\r\n")

    # write sensor data
    row = [helpers.datetime_string()]
    for key in sensors():
      row.append(str(readings[key]))
    f.write(",".join(row) + "\r\n")


# returns true if the button is held for the number of seconds provided
def button_held_for(seconds):
  start = time.time()
  while button_pin.value():
    if time.time() - start > seconds:
      return True
    time.sleep(0.1)



def warn_led(state):
  if state == WARN_LED_OFF:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_OFF)
  elif state == WARN_LED_ON:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_1024HZ)
  elif state == WARN_LED_BLINK:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_1HZ)
    
# the pcf85063a defaults to 32KHz clock output so
# we need to explicitly turn that off by default
warn_led(WARN_LED_OFF)

def get_date_str(self):
  datetime = rtc.datetime()
  return "{:04}-{:02}-{:02}".format(datetime[0], datetime[1], datetime[2])

def get_datetime_str(self):
  datetime = rtc.datetime()
  return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6])

def activity_led(brightness):
  brightness = max(0, min(100, brightness)) # clamp to range
  # gamma correct the brightness (gamma 2.8)
  value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
  activity_led_pwm.duty_u16(value)
  
def activity_led_callback(t):
  # updates the activity led brightness based on a sinusoid seeded by the current time
  activity_led((math.sin(time.ticks_ms() * math.pi * 2 / (1000 / activity_led_pulse_speed_hz)) * 40) + 60)

def pulse_activity_led(speed_hz = 1):
  global activity_led_timer, activity_led_pulse_speed_hz
  activity_led_pulse_speed_hz = speed_hz
  stop_activity_led() # if led already active then kill timer
  activity_led_timer.init(period=50, mode=Timer.PERIODIC, callback=activity_led_callback)

def stop_activity_led():
  global activity_led_timer
  activity_led_timer.deinit()
  activity_led(0)


def get_wake_reason():
  wake_reason = None
  if button_pin.value():
    wake_reason = WAKE_REASON_BUTTON_PRESS
  elif rtc_alarm_pin.value():
    wake_reason = WAKE_REASON_RTC_ALARM
  elif not external_trigger_pin.value():
    wake_reason = WAKE_REASON_EXTERNAL_TRIGGER


  return wake_reason

def wake_reason_name(wake_reason):
  wake_reason_names = {
    None: "unknown",
    WAKE_REASON_PROVISION: "provisioning",
    WAKE_REASON_BUTTON_PRESS: "button",
    WAKE_REASON_RTC_ALARM: "rtc_alarm",
    WAKE_REASON_EXTERNAL_TRIGGER: "external_trigger",
    WAKE_REASON_RAIN_TRIGGER: "rain_sensor"
  }

  if wake_reason in wake_reason_names:
    return wake_reason_names[wake_reason]
  return None



# guess which type of board this is based on the devices on the i2c bus
# and state of certain pins at startup
def detect_model():
  # determine which type of board is connected
  i2c_devices = i2c.scan()

  result = None
  if 56 in i2c_devices: # 56 = colour / light sensor and only present on Indoor
    result = "indoor"
  elif 35 in i2c_devices: # 35 = ltr-599 on grow & weather
    # the wind vane pin is pulled high with a 10k resistor on the weather
    # board - we can detect this and disambiguate using it
    pump1_pin = Pin(10, Pin.IN, Pin.PULL_UP)
    result = "grow" if pump1_pin.value() == False else "weather"
    # disable the pull up (otherwise this keeps the weather board awake)
    pump1_pin.init(pull=None)
  else:
    # otherwise it's urban, we'll need to add camera in the future too...
    result = "urban"

  return result


def reset():
  machine.reset()

# import board specific methods
model = detect_model()
if model == "indoor":
  from enviro.boards.indoor import sensors, get_sensor_readings
if model == "grow":
  from enviro.boards.grow import sensors, get_sensor_readings
if model == "weather":
  from enviro.boards.weather import sensors, get_sensor_readings
if model == "urban":
  from enviro.boards.urban import sensors, get_sensor_readings

destination = helpers.get_config("destination")
if destination == "http":
  from enviro.destinations.http import upload_readings
if destination == "mqtt":
  from enviro.destinations.mqtt import upload_readings
if destination == "adafruit_io":
  from enviro.destinations.adafruit_io import upload_readings

def startup():
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
  pulse_activity_led(0.5)

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
  rtc.clear_timer_flag()
  rtc.clear_alarm_flag()

  # if wake time supplied then set rtc timer
  if minutes != -1:
    logging.info(f"  - setting timer to wake in {minutes} minutes")
    rtc.enable_timer_interrupt(True)
    rtc.set_timer(minutes, PCF85063A.TIMER_TICK_1_OVER_60HZ)  

  # disable the vsys hold, causing us to turn off
  logging.info("  - shutting down")
  hold_vsys_en_pin.init(Pin.IN)

  # if we're still awake it means power is coming from the USB port in which
  # case we can't (and don't need to) sleep.
  stop_activity_led()

  # we'll wait here until the rtc timer triggers and then reset the board
  logging.debug("  - on usb power (so can't shutdown) halt and reset instead")
  while not rtc.read_timer_flag():    
    time.sleep(0.1)

  logging.debug("  - hard reset")

  # reset the board
  reset()