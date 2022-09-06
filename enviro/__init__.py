# keep the power rail alive by holding VSYS_EN high as early as possible
# ===========================================================================
from enviro.constants import *
from machine import Pin
hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT, value=True)

# detect board model based on devices on the i2c bus and pin state
# ===========================================================================
from pimoroni_i2c import PimoroniI2C
i2c = PimoroniI2C(I2C_SDA_PIN, I2C_SCL_PIN, 100000)
i2c_devices = i2c.scan()
model = None
if 56 in i2c_devices: # 56 = colour / light sensor and only present on Indoor
  model = "indoor"
elif 35 in i2c_devices: # 35 = ltr-599 on grow & weather
  pump3_pin = Pin(12, Pin.IN, Pin.PULL_UP)
  model = "grow" if pump3_pin.value() == False else "weather"    
  pump3_pin.init(pull=None)
else:    
  model = "urban" # otherwise it's urban..

# return the module that implements this board type
def get_board():
  if model == "indoor":
    import enviro.boards.indoor as board
  if model == "grow":
    import enviro.boards.grow as board
  if model == "weather":
    import enviro.boards.weather as board
  if model == "urban":
    import enviro.boards.urban as board
  return board
  
# set up the activity led
# ===========================================================================
from machine import PWM, Timer
import math
activity_led_pwm = PWM(Pin(ACTIVITY_LED_PIN))
activity_led_pwm.freq(1000)
activity_led_pwm.duty_u16(0)

# set the brightness of the activity led
def activity_led(brightness):
  brightness = max(0, min(100, brightness)) # clamp to range
  # gamma correct the brightness (gamma 2.8)
  value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
  activity_led_pwm.duty_u16(value)
  
activity_led_timer = Timer(-1)
activity_led_pulse_speed_hz = 1
def activity_led_callback(t):
  # updates the activity led brightness based on a sinusoid seeded by the current time
  brightness = (math.sin(time.ticks_ms() * math.pi * 2 / (1000 / activity_led_pulse_speed_hz)) * 40) + 60
  value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
  activity_led_pwm.duty_u16(value)

# set the activity led into pulsing mode
def pulse_activity_led(speed_hz = 1):
  global activity_led_timer, activity_led_pulse_speed_hz
  activity_led_pulse_speed_hz = speed_hz
  activity_led_timer.deinit()
  activity_led_timer.init(period=50, mode=Timer.PERIODIC, callback=activity_led_callback)

# turn off the activity led and disable any pulsing animation that's running
def stop_activity_led():
  global activity_led_timer
  activity_led_timer.deinit()
  activity_led_pwm.duty_u16(0)

# check whether device needs provisioning
# ===========================================================================
import time
from phew import logging
button_pin = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
needs_provisioning = False
start = time.time()
while button_pin.value(): # button held for 3 seconds go into provisioning
  if time.time() - start > 3:
    needs_provisioning = True
    break

try:
  import config # fails to import (missing/corrupt) go into provisioning
  if not config.provisioned: # provisioned flag not set go into provisioning
    needs_provisioning = True
except Exception as e:
  logging.error("> missing or corrupt config.py", e)
  needs_provisioning = True

if needs_provisioning:
  logging.info("> entering provisioning mode")
  import enviro.provisioning
  # control never returns to here, provisioning takes over completely

# all the other imports, so many shiny modules
import machine, sys, os, json
from machine import RTC, ADC
import phew
from pcf85063a import PCF85063A
import enviro.helpers as helpers

# read battery voltage - we have to toggle the wifi chip select
# pin to take the reading - this is probably not ideal but doesn't
# seem to cause issues. there is no obvious way to shut down the
# wifi for a while properly to do this (wlan.disonnect() and
# wlan.active(False) both seem to mess things up big style..)
old_state = Pin(WIFI_CS_PIN).value()
Pin(WIFI_CS_PIN, Pin.OUT, value=True)
sample_count = 10
battery_voltage = 0
for i in range(0, sample_count):
  battery_voltage += (ADC(29).read_u16() * 3.3 / 65535) * 3
battery_voltage /= sample_count
battery_voltage = round(battery_voltage, 3)
Pin(WIFI_CS_PIN).value(old_state)

# set up the button, external trigger, and rtc alarm pins
rtc_alarm_pin = Pin(RTC_ALARM_PIN, Pin.IN, Pin.PULL_DOWN)
external_trigger_pin = Pin(EXTERNAL_INTERRUPT_PIN, Pin.IN, Pin.PULL_DOWN)

# intialise the pcf85063a real time clock chip
rtc = PCF85063A(i2c)
i2c.writeto_mem(0x51, 0x00, b'\x00') # ensure rtc is running (this should be default?)
rtc.enable_timer_interrupt(False)

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



def connect_to_wifi():
  if phew.is_connected_to_wifi():
    logging.info(f"> already connected to wifi")
    return True

  wifi_ssid = config.wifi_ssid
  wifi_password = config.wifi_password

  logging.info(f"> connecting to wifi network '{wifi_ssid}'")
  ip = phew.connect_to_wifi(wifi_ssid, wifi_password, timeout_seconds=30)

  if not ip:
    logging.error(f"! failed to connect to wireless network {wifi_ssid}")
    return False

  logging.info("  - ip address: ", ip)

  return True

# returns the reason we woke up
def wake_reason():
  reason = get_wake_reason()
  return wake_reason_name(reason)

# log the error, blink the warning led, and go back to sleep
def halt(message):
  logging.error(message)
  warn_led(WARN_LED_BLINK)
  sleep()

# returns True if we've used up 90% of the internal filesystem
def low_disk_space():
  if not phew.remote_mount: # os.statvfs doesn't exist on remote mounts
    return (os.statvfs(".")[3] / os.statvfs(".")[2]) < 0.1   
  return False

# returns True if the rtc clock has been set
def is_clock_set():
  return rtc.datetime()[0] > 2020 # year greater than 2020? we're golden!

# connect to wifi and attempt to fetch the current time from an ntp server
def sync_clock_from_ntp():
  from phew import ntp
  if not connect_to_wifi():
    return False
  timestamp = ntp.fetch()
  if not timestamp:
    return False  
  rtc.datetime(timestamp) # set the time on the rtc chip
  return True

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
  return names.get(wake_reason)

# get the readings from the on board sensors
def get_sensor_readings():
  readings = get_board().get_sensor_readings()
  readings["voltage"] = battery_voltage
  return readings

# save the provided readings into a todays readings data file
def save_reading(readings):
  # open todays reading file and save readings
  helpers.mkdir_safe("readings")
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


# save the provided readings into a cache file for future uploading
def cache_upload(readings):
  payload = {
    "nickname": config.nickname,
    "timestamp": helpers.datetime_string(),
    "readings": readings,
    "model": model,
    "uid": helpers.uid()
  }
  uploads_filename = f"uploads/{helpers.datetime_string()}.json"
  helpers.mkdir_safe("uploads")
  with open(uploads_filename, "w") as upload_file:
    json.dump(payload, upload_file)

# return the number of cached results waiting to be uploaded
def cached_upload_count():
  return len(os.listdir("uploads"))

# returns True if we have more cached uploads than our config allows
def is_upload_needed():
  return cached_upload_count() >= config.upload_frequency

# upload cached readings to the configured destination
def upload_readings():
  if not connect_to_wifi():
    return False

  destination = config.destination
  exec(f"import enviro.destinations.{destination}")
  destination_module = sys.modules[f"enviro.destinations.{destination}"]
  for cache_file in os.ilistdir("uploads"):
    with open(f"uploads/{cache_file[0]}", "r") as upload_file:
      success = destination_module.upload_reading(json.load(upload_file))
      if not success:
        logging.error(f"! failed to upload '{cache_file[0]}' to {destination}")
        return False

      # remove the cache file now uploaded
      logging.info(f"  - uploaded {cache_file[0]} to {destination}")
    
    os.remove(f"uploads/{cache_file[0]}")
        
  return True

def startup():
  # write startup banner into log file
  logging.debug("> performing startup")

  # give each board a chance to perform any startup it needs
  # ===========================================================================
  board = get_board()
  if hasattr(board, "startup"):
    board.startup()

  # log the wake reason
  logging.info("  - wake reason:", wake_reason())

  # also immediately turn on the LED to indicate that we're doing something
  logging.debug("  - turn on activity led")
  pulse_activity_led(0.5)

def sleep():
  logging.info("> going to sleep")

  # make sure the rtc flags are cleared before going back to sleep
  logging.debug("  - clearing and disabling timer and alarm")
  rtc.clear_alarm_flag()

  # set alarm to wake us up for next reading
  dt = rtc.datetime()
  hour, minute = dt[3:5]

  # calculate how many minutes into the day we are
  minute = math.floor(minute / config.reading_frequency) * config.reading_frequency
  minute += config.reading_frequency
  while minute >= 60:      
    minute -= 60
    hour += 1
  if hour >= 24:
    hour -= 24
  ampm = "am" if hour < 12 else "pm"

  logging.info(f"  - setting alarm to wake at {hour:02}:{minute:02}{ampm}")

  # sleep until next scheduled reading
  rtc.set_alarm(0, minute, hour)
  rtc.enable_alarm_interrupt(True)

  # disable the vsys hold, causing us to turn off
  logging.info("  - shutting down")
  hold_vsys_en_pin.init(Pin.IN)

  # if we're still awake it means power is coming from the USB port in which
  # case we can't (and don't need to) sleep.
  stop_activity_led()

  # if running via mpremote/pyboard.py with a remote mount then we can't
  # reset the board so just exist
  if phew.remote_mount:
    sys.exit()

  # we'll wait here until the rtc timer triggers and then reset the board
  logging.debug("  - on usb power (so can't shutdown) halt and reset instead")
  while not rtc.read_alarm_flag():    
    time.sleep(0.25)

    if button_pin.value(): # allow button to force reset
      break

  logging.debug("  - reset")

  # reset the board
  machine.reset()