# keep the power rail alive by holding VSYS_EN high as early as possible
from enviro.constants import *
from machine import Pin
hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT, value=True)

# all the other imports, so many shiny modules
import math, time, machine, sys, os, ujson
from machine import Timer, PWM, RTC, ADC
from phew import logging, remote_mount
from pimoroni_i2c import PimoroniI2C
from pcf85063a import PCF85063A
import enviro.helpers as helpers

# read battery voltage - we have to toggle the wifi chip select
# pin to take the reading - this is probably not ideal but doesn't
# seem to cause issues. there is no obvious way to shut down the
# wifi for a while properly to do this (wlan.disonnect() and
# wlan.active(False) both seem to mess things up big style..)
old_state = Pin(WIFI_CS_PIN).value()
Pin(WIFI_CS_PIN, Pin.OUT, value=True)
battery_voltage = round((ADC(29).read_u16() * 3.3 / 65535) * 3, 3)
Pin(WIFI_CS_PIN).value(old_state)

# set up the button, external trigger, and rtc alarm pins
button_pin = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
rtc_alarm_pin = Pin(RTC_ALARM_PIN, Pin.IN, Pin.PULL_DOWN)
external_trigger_pin = Pin(EXTERNAL_INTERRUPT_PIN, Pin.IN, Pin.PULL_DOWN)

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
i2c.writeto_mem(0x51, 0x00, b'\x00') # ensure rtc is running (this should be default?)
t = rtc.datetime()
RTC().datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0)) # synch PR2040 rtc too

# jazz up that console! toot toot!
print("       ___            ___            ___          ___          ___            ___       ")
print("      /  /\          /__/\          /__/\        /  /\        /  /\          /  /\      ")
print("     /  /:/_         \  \:\         \  \:\      /  /:/       /  /::\        /  /::\     ")
print("    /  /:/ /\         \  \:\         \  \:\    /  /:/       /  /:/\:\      /  /:/\:\    ")
print("   /  /:/ /:/_    _____\__\:\    ___  \  \:\  /__/::\      /  /:/~/:/     /  /:/  \:\   ")
print("  /__/:/ /:/ /\  /__/::::::::\  /___\  \__\:\ \__\/\:\__  /__/:/ /:/___  /__/:/ \__\:\  ")
print("  \  \:\/:/ /:/  \  \:\~~~__\/  \  \:\ |  |:|    \  \:\/\ \  \:\/:::::/  \  \:\ /  /:/  ")
print("   \  \::/ /:/    \  \:\         \  \:\|  |:|     \__\::/  \  \::/~~~`    \  \:\  /:/   ")
print("    \  \:\/:/      \  \:\         \  \:\__|:|     /  /:/    \  \:\         \  \:\/:/    ")
print("     \  \::/        \  \:\         \  \::::/     /__/:/      \  \:\         \  \::/     ")
print("      \__\/          \__\/          `~~~~~`      \__\/        \__\/          \__\/      ")
print("")
print("    -  --  ---- -----=--==--===  hey enviro, let's go!  ===--==--=----- ----  --  -     ")
print("")

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

def provision():
  # this import starts the provisioning process and control will never 
  # return from here
  import enviro.provisioning

# returns the reason we woke up
def wake_reason():
  reason = get_wake_reason()
  return wake_reason_name(reason)

# log the error, blink the warning led, and go back to sleep
def halt(message):
  logging.error(message)
  warn_led(WARN_LED_BLINK)
  sleep(config.reading_frequency)

# returns True if we've used up 90% of the internal filesystem
def low_disk_space():
  if not remote_mount: # os.statvfs doesn't exist on remote mounts
    return (os.statvfs(".")[3] / os.statvfs(".")[2]) < 0.1   
  return False

# returns True if the rtc clock has been set
def is_clock_set():
  return rtc.datetime()[0] > 2020 # year greater than 2020? we're golden!

# connect to wifi and attempt to fetch the current time from an ntp server
def sync_clock_from_ntp():
  from phew import ntp
  if not helpers.connect_to_wifi():
    return False
  timestamp = ntp.fetch()
  if not timestamp:
    return False  
  rtc.datetime(timestamp) # set the time on the rtc chip
  return True

# returns true if the button is held for the number of seconds provided
def button_held_for(seconds):
  start = time.time()
  while button_pin.value():
    if time.time() - start > seconds:
      return True
    time.sleep(0.1)
  return False

# set the state of the warning led (off, on, blinking)
def warn_led(state):
  if state == WARN_LED_OFF:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_OFF)
  elif state == WARN_LED_ON:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_1024HZ)
  elif state == WARN_LED_BLINK:
    rtc.set_clock_output(PCF85063A.CLOCK_OUT_1HZ)
    
# the pcf85063a defaults to 32KHz clock output so need to explicitly turn off
warn_led(WARN_LED_OFF)

# set the brightness of the activity led
def activity_led(brightness):
  stop_activity_led()
  brightness = max(0, min(100, brightness)) # clamp to range
  # gamma correct the brightness (gamma 2.8)
  value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
  activity_led_pwm.duty_u16(value)
  
def activity_led_callback(t):
  # updates the activity led brightness based on a sinusoid seeded by the current time
  activity_led((math.sin(time.ticks_ms() * math.pi * 2 / (1000 / activity_led_pulse_speed_hz)) * 40) + 60)

# set the activity led into pulsing mode
def pulse_activity_led(speed_hz = 1):
  global activity_led_timer, activity_led_pulse_speed_hz
  activity_led_pulse_speed_hz = speed_hz
  stop_activity_led() # if led already active then kill timer
  activity_led_timer.init(period=50, mode=Timer.PERIODIC, callback=activity_led_callback)

# turn off the activity led and disable any pulsing animation that's running
def stop_activity_led():
  global activity_led_timer
  activity_led_timer.deinit()
  activity_led_pwm.duty_u16(0)

# returns the reason the board woke up from deep sleep
def get_wake_reason():
  wake_reason = None
  if button_pin.value():
    wake_reason = WAKE_REASON_BUTTON_PRESS
  elif rtc_alarm_pin.value():
    wake_reason = WAKE_REASON_RTC_ALARM
  elif not external_trigger_pin.value():
    wake_reason = WAKE_REASON_EXTERNAL_TRIGGER
  return wake_reason

# convert a wake reason into it's name
def wake_reason_name(wake_reason):
  names = {
    None: "unknown",
    WAKE_REASON_PROVISION: "provisioning",
    WAKE_REASON_BUTTON_PRESS: "button",
    WAKE_REASON_RTC_ALARM: "rtc_alarm",
    WAKE_REASON_EXTERNAL_TRIGGER: "external_trigger",
    WAKE_REASON_RAIN_TRIGGER: "rain_sensor"
  }
  return names[wake_reason] if wake_reason in names else None

# guess board type based on devices on the i2c bus and pin state
def detect_model():  
  i2c_devices = i2c.scan()
  result = None
  if 56 in i2c_devices: # 56 = colour / light sensor and only present on Indoor
    result = "indoor"
  elif 35 in i2c_devices: # 35 = ltr-599 on grow & weather
    pump1_pin = Pin(10, Pin.IN, Pin.PULL_UP)
    result = "grow" if pump1_pin.value() == False else "weather"    
    pump1_pin.init(pull=None) # disable the pull up (or weather stays awake)
  else:    
    result = "urban" # otherwise it's urban..
  return result

# return the module that implements this board type
def get_board():
  model = detect_model()
  if model == "indoor":
    import enviro.boards.indoor as board
  if model == "grow":
    import enviro.boards.grow as board
  if model == "weather":
    import enviro.boards.weather as board
  if model == "urban":
    import enviro.boards.urban as board
  return board

# get the readings from the on board sensors
def get_sensor_readings():
  readings = get_board().get_sensor_readings()
  readings["voltage"] = battery_voltage
  return readings

# save the provided readings into a todays readings data file
def save_reading(readings):
  # open todays reading file and save readings
  readings_filename = f"readings/{helpers.date_string()}.txt"
  new_file = not helpers.file_exists(readings_filename)
  with open(readings_filename, "a") as f:
    if new_file:
      # new readings file so write out column headings first
      f.write("timestamp," + ",".join(readings.keys()) + "\r\n")
    # write sensor data
    row = [helpers.datetime_string()]
    for key in readings.keys():
      row.append(str(readings[key]))
    f.write(",".join(row) + "\r\n")

  # is an upload destination set? if so cache this reading for upload too
  if helpers.get_config("destination"):
    cache_upload(readings)

# save the provided readings into a cache file for future uploading
def cache_upload(readings):
  payload = {
    "nickname": helpers.get_config("nickname"),
    "timestamp": helpers.datetime_string(),
    "readings": readings,
    "model": detect_model(),
    "uid": helpers.uid()
  }
  uploads_filename = f"uploads/{helpers.datetime_string()}.json"
  with open(uploads_filename, "w") as f:
    f.write(ujson.dumps(payload))

# return the number of cached results waiting to be uploaded
def cached_upload_count():
  return len(os.listdir("uploads"))

# returns True if we have more cached uploads than our config allows
def is_upload_needed():
  return cached_upload_count() >= helpers.get_config("upload_frequency")

# upload cached readings to the configured destination
def upload_readings():
  if not helpers.connect_to_wifi():
    return False
  destination = helpers.get_config("destination")
  if destination == "http":
    import enviro.destinations.http as destination
  if destination == "mqtt":
    import enviro.destinations.mqtt as destination
  if destination == "adafruit_io":
    import enviro.destinations.adafruit_io as destination
  return destination.upload_readings()

def startup():
  # write startup banner into log file
  logging.debug("> performing startup")

  # log the wake reason
  logging.info("  - wake reason:", wake_reason())

  # also immediately turn on the LED to indicate that we're doing something
  logging.debug("  - turn on activity led")
  pulse_activity_led(0.5)

  # if button held for 3 seconds on startup then go into provisioning mode
  user_requested_provisioning = button_held_for(3)

  # if enviro isn't configured or the user requested provisioning then
  # put the board into provisioning (setup) mode
  if user_requested_provisioning or needs_provisioning():
    logging.info("> entering provisioning mode")
    provision()
    # control never returns to here, provisioning takes over comp letely

  # ensure we have a directory to store reading and upload files
  helpers.mkdir_safe("readings")
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

  # if running via mpremote/pyboard.py with a remote mount then we can't
  # reset the board so just exist
  if remote_mount:
    sys.exit()

  # we'll wait here until the rtc timer triggers and then reset the board
  logging.debug("  - on usb power (so can't shutdown) halt and reset instead")
  while not rtc.read_timer_flag():    
    time.sleep(0.25)

    if button_pin.value(): # allow button to force reset
      break

  logging.debug("  - reset")

  # reset the board
  machine.reset()