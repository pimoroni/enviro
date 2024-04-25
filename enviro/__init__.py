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
import machine, sys, os, ujson
from machine import RTC, ADC
import phew
from pcf85063a import PCF85063A
import enviro.config_defaults as config_defaults
import enviro.helpers as helpers

config_defaults.add_missing_config_settings()

# read the state of vbus to know if we were woken up by USB
vbus_present = Pin("WL_GPIO2", Pin.IN).value()

#BUG Temporarily disabling battery reading, as it seems to cause issues when connected to Thonny
"""
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
"""

# set up the button, external trigger, and rtc alarm pins
rtc_alarm_pin = Pin(RTC_ALARM_PIN, Pin.IN, Pin.PULL_DOWN)
# BUG This should only be set up for Enviro Camera
# external_trigger_pin = Pin(EXTERNAL_INTERRUPT_PIN, Pin.IN, Pin.PULL_DOWN)

# intialise the pcf85063a real time clock chip
rtc = PCF85063A(i2c)
i2c.writeto_mem(0x51, 0x00, b'\x00') # ensure rtc is running (this should be default?)
rtc.enable_timer_interrupt(False)

t = rtc.datetime()
# BUG ERRNO 22, EINVAL, when date read from RTC is invalid for the pico's RTC.
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

def reconnect_wifi(ssid, password, country, hostname=None):
  import time
  import network
  import math
  import rp2
  import ubinascii
  
  start_ms = time.ticks_ms()

  # Set country
  rp2.country(country)

  # Set hostname
  if hostname is None:
      hostname = f"EnviroW-{helpers.uid()[-4:]}"
  network.hostname(hostname)

  # Reference: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
  CYW43_LINK_DOWN = 0
  CYW43_LINK_JOIN = 1
  CYW43_LINK_NOIP = 2
  CYW43_LINK_UP = 3
  CYW43_LINK_FAIL = -1
  CYW43_LINK_NONET = -2
  CYW43_LINK_BADAUTH = -3

  status_names = {
    CYW43_LINK_DOWN: "Link is down",
    CYW43_LINK_JOIN: "Connected to wifi",
    CYW43_LINK_NOIP: "Connected to wifi, but no IP address",
    CYW43_LINK_UP: "Connect to wifi with an IP address",
    CYW43_LINK_FAIL: "Connection failed",
    CYW43_LINK_NONET: "No matching SSID found (could be out of range, or down)",
    CYW43_LINK_BADAUTH: "Authenticatation failure",
  }

  wlan = network.WLAN(network.STA_IF)

  def dump_status():
    status = wlan.status()
    logging.info(f"> active: {1 if wlan.active() else 0}, status: {status} ({status_names[status]})")
    return status

  # Return True on expected status, exception on error status (negative) and False on timeout
  def wait_status(expected_status, *, timeout=10, tick_sleep=0.5):
    for i in range(math.ceil(timeout / tick_sleep)):
      time.sleep(tick_sleep)
      status = dump_status()
      if status == expected_status:
        return True
      if status < 0:
        raise Exception(status_names[status])
    return False

  wlan.active(True)
  # Disable power saving mode if on USB power
  if vbus_present:
    wlan.config(pm=0xa11140)

  # Print MAC
  mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
  logging.info("> MAC: " + mac)
  
  # Disconnect when necessary
  status = dump_status()
  if status >= CYW43_LINK_JOIN and status < CYW43_LINK_UP:
    logging.info("> Disconnecting...")
    wlan.disconnect()
    try:
      wait_status(CYW43_LINK_DOWN)
    except Exception as x:
      raise Exception(f"Failed to disconnect: {x}")
  logging.info("> Ready for connection!")

  # Connect to our AP
  logging.info(f"> Connecting to SSID {ssid} (password: {password})...")
  wlan.connect(ssid, password)
  try:
    wait_status(CYW43_LINK_UP)
  except Exception as x:
    raise Exception(f"Failed to connect to SSID {ssid} (password: {password}): {x}")
  logging.info("> Connected successfully!")

  ip, subnet, gateway, dns = wlan.ifconfig()
  logging.info(f"> IP: {ip}, Subnet: {subnet}, Gateway: {gateway}, DNS: {dns}")
  
  elapsed_ms = time.ticks_ms() - start_ms
  logging.info(f"> Elapsed: {elapsed_ms}ms")
  return elapsed_ms

def connect_to_wifi():
  try:
    logging.info(f"> connecting to wifi network '{config.wifi_ssid}'")
    elapsed_ms = reconnect_wifi(config.wifi_ssid, config.wifi_password, config.wifi_country)
    # a slow connection time will drain the battery faster and may
    # indicate a poor quality connection
    seconds_to_connect = elapsed_ms / 1000
    if seconds_to_connect > 5:
      logging.warn("  - took", seconds_to_connect, "seconds to connect to wifi")
    return True
  except Exception as x:
    logging.error(f"! {x}")
    return False

# log the error, blink the warning led, and go back to sleep
def halt(message):
  logging.error(message)
  warn_led(WARN_LED_BLINK)
  sleep()

# log the exception, blink the warning led, and go back to sleep
def exception(exc):
  import sys, io
  buf = io.StringIO()
  sys.print_exception(exc, buf)
  logging.exception("! " + buf.getvalue())
  warn_led(WARN_LED_BLINK)
  sleep()

# returns True if we've used up 90% of the internal filesystem
def low_disk_space():
  if not phew.remote_mount: # os.statvfs doesn't exist on remote mounts
    return (os.statvfs(".")[3] / os.statvfs(".")[2]) < 0.1   
  return False

# returns True if the rtc clock has been set recently 
def is_clock_set():
  # is the year on or before 2020?
  if rtc.datetime()[0] <= 2020:
    return False

  if helpers.file_exists("sync_time.txt"):
    now_str = helpers.datetime_string()
    now = helpers.timestamp(now_str)

    time_entries = []
    with open("sync_time.txt", "r") as timefile:
      time_entries = timefile.read().split("\n")

    # read the first line from the time file
    sync = now
    for entry in time_entries:
      if entry:
        sync = helpers.timestamp(entry)
        break

    seconds_since_sync = now - sync
    if seconds_since_sync >= 0:  # there's the rare chance of having a newer sync time than what the RTC reports
      try:
        if seconds_since_sync < (config.resync_frequency * 60 * 60):
          return True

        logging.info(f"  - rtc has not been synched for {config.resync_frequency} hour(s)")
      except AttributeError:
        return True

  return False

# connect to wifi and attempt to fetch the current time from an ntp server
def sync_clock_from_ntp():
  from phew import ntp
  if not connect_to_wifi():
    return False
  #TODO Fetch only does one attempt. Can also optionally set Pico RTC (do we want this?)
  timestamp = ntp.fetch()
  if not timestamp:
    logging.error("  - failed to fetch time from ntp server")
    return False  

  # fixes an issue where sometimes the RTC would not pick up the new time
  i2c.writeto_mem(0x51, 0x00, b'\x10') # reset the rtc so we can change the time
  rtc.datetime(timestamp) # set the time on the rtc chip
  i2c.writeto_mem(0x51, 0x00, b'\x00') # ensure rtc is running
  rtc.enable_timer_interrupt(False)

  # read back the RTC time to confirm it was updated successfully
  dt = rtc.datetime()
  if dt != timestamp[0:7]:
    logging.error("  - failed to update rtc")
    if helpers.file_exists("sync_time.txt"):
      os.remove("sync_time.txt")
    return False

  logging.info("  - rtc synched")
  
  # write out the sync time log
  with open("sync_time.txt", "w") as syncfile:
    syncfile.write("{0:04d}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}Z".format(*timestamp))  

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
  import wakeup
  
  wake_reason = None
  if wakeup.get_gpio_state() & (1 << BUTTON_PIN):
    wake_reason = WAKE_REASON_BUTTON_PRESS
  elif wakeup.get_gpio_state() & (1 << RTC_ALARM_PIN):
    wake_reason = WAKE_REASON_RTC_ALARM
  # TODO Temporarily removing this as false reporting on non-camera boards
  #elif not external_trigger_pin.value():
  #  wake_reason = WAKE_REASON_EXTERNAL_TRIGGER
  elif vbus_present:
    wake_reason = WAKE_REASON_USB_POWERED
  return wake_reason

# convert a wake reason into it's name
def wake_reason_name(wake_reason):
  names = {
    None: "unknown",
    WAKE_REASON_PROVISION: "provisioning",
    WAKE_REASON_BUTTON_PRESS: "button",
    WAKE_REASON_RTC_ALARM: "rtc_alarm",
    WAKE_REASON_EXTERNAL_TRIGGER: "external_trigger",
    WAKE_REASON_RAIN_TRIGGER: "rain_sensor",
    WAKE_REASON_USB_POWERED: "usb_powered"
  }
  return names.get(wake_reason)

# get the readings from the on board sensors
def get_sensor_readings():
  seconds_since_last = 0
  now_str = helpers.datetime_string()
  if helpers.file_exists("last_time.txt"):
    now = helpers.timestamp(now_str)

    time_entries = []
    with open("last_time.txt", "r") as timefile:
      time_entries = timefile.read().split("\n")

    # read the first line from the time file
    last = now
    for entry in time_entries:
      if entry:
        last = helpers.timestamp(entry)
        break

    seconds_since_last = now - last
    logging.info(f"  - seconds since last reading: {seconds_since_last}")


  readings = get_board().get_sensor_readings(seconds_since_last, vbus_present)
  # readings["voltage"] = 0.0 # battery_voltage #Temporarily removed until issue is fixed

  # write out the last time log
  with open("last_time.txt", "w") as timefile:
    timefile.write(now_str)  

  return readings

# save the provided readings into a todays readings data file
def save_reading(readings):
  # open todays reading file and save readings
  helpers.mkdir_safe("readings")
  readings_filename = f"readings/{helpers.date_string()}.csv"
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

  uploads_filename = f"uploads/{helpers.datetime_file_string()}.json"
  helpers.mkdir_safe("uploads")
  with open(uploads_filename, "w") as upload_file:
    #json.dump(payload, upload_file) # TODO what it was changed to
    upload_file.write(ujson.dumps(payload))

# return the number of cached results waiting to be uploaded
def cached_upload_count():
  try:
    return len(os.listdir("uploads"))
  except OSError:
    return 0

# returns True if we have more cached uploads than our config allows
def is_upload_needed():
  return cached_upload_count() >= config.upload_frequency

# upload cached readings to the configured destination
def upload_readings():
  if not connect_to_wifi():
    logging.error(f"  - cannot upload readings, wifi connection failed")
    return False

  destination = config.destination
  try:
    exec(f"import enviro.destinations.{destination}")
    destination_module = sys.modules[f"enviro.destinations.{destination}"]
    destination_module.log_destination()

    for cache_file in os.ilistdir("uploads"):
      try:
        with open(f"uploads/{cache_file[0]}", "r") as upload_file:
          status = destination_module.upload_reading(ujson.load(upload_file))
          if status == UPLOAD_SUCCESS:
            os.remove(f"uploads/{cache_file[0]}")
            logging.info(f"  - uploaded {cache_file[0]}")
          elif status == UPLOAD_RATE_LIMITED:
            # write out that we want to attempt a reupload
            with open("reattempt_upload.txt", "w") as attemptfile:
              attemptfile.write("")

            logging.info(f"  - cannot upload '{cache_file[0]}' - rate limited")
            sleep(1)
          elif status == UPLOAD_LOST_SYNC:
            # remove the sync time file to trigger a resync on next boot
            if helpers.file_exists("sync_time.txt"):
              os.remove("sync_time.txt")
             
            # write out that we want to attempt a reupload
            with open("reattempt_upload.txt", "w") as attemptfile:
              attemptfile.write("")

            logging.info(f"  - cannot upload '{cache_file[0]}' - rtc has become out of sync")
            sleep(1)
          elif status == UPLOAD_SKIP_FILE:
            logging.error(f"  ! cannot upload '{cache_file[0]}' to {destination}. Skipping file")
            warn_led(WARN_LED_BLINK)
            continue
          else:
            logging.error(f"  ! failed to upload '{cache_file[0]}' to {destination}")
            return False

      except OSError:
        logging.error(f"  ! failed to open '{cache_file[0]}'")
        return False

      except KeyError:
        logging.error(f"  ! skipping '{cache_file[0]}' as it is missing data. It was likely created by an older version of the enviro firmware")
        
  except ImportError:
    logging.error(f"! cannot find destination {destination}")
    return False

  finally:
    # Disconnect wifi
    import network
    logging.info("> Disconnecting wireless after upload")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.active(False)

  return True

# HASS Discovery
def hass_discovery():
  destination = config.destination
  try:
    exec(f"import enviro.destinations.{destination}")
    destination_module = sys.modules[f"enviro.destinations.{destination}"]
    destination_module.hass_discovery(model)
    config.hass_discovery_triggered = True
  except ImportError:
    logging.error(f"! cannot find destination {destination}")
    return False
  except:
      logging.error(f"Unknown error in setting HASS Discovery")

def startup():
  import sys

  # write startup info into log file
  logging.info("> performing startup")
  logging.debug(f"  - running Enviro {ENVIRO_VERSION}, {sys.version.split('; ')[1]}")

  # get the reason we were woken up
  reason = get_wake_reason()

  # give each board a chance to perform any startup it needs
  # ===========================================================================
  board = get_board()
  if hasattr(board, "startup"):
    continue_startup = board.startup(reason)
    # put the board back to sleep if the startup doesn't need to continue
    # and the RTC has not triggered since we were awoken
    if not continue_startup and not rtc.read_alarm_flag():
      logging.debug("  - wake reason: trigger")
      sleep()

  # log the wake reason
  logging.info("  - wake reason:", wake_reason_name(reason))

  # also immediately turn on the LED to indicate that we're doing something
  logging.debug("  - turn on activity led")
  pulse_activity_led(0.5)

  # see if we were woken to attempt a reupload
  if helpers.file_exists("reattempt_upload.txt"):
    upload_count = cached_upload_count()
    if upload_count == 0:
      os.remove("reattempt_upload.txt")
      return

    logging.info(f"> {upload_count} cache file(s) still to upload")
    if not upload_readings():
      halt("! reading upload failed")

    os.remove("reattempt_upload.txt")

    # if it was the RTC that woke us, go to sleep until our next scheduled reading
    # otherwise continue with taking new readings etc
    # Note, this *may* result in a missed reading
    if reason == WAKE_REASON_RTC_ALARM:
      sleep()

def sleep(time_override=None):
  if time_override is not None:
    logging.info(f"> going to sleep for {time_override} minute(s)")
  else:
    logging.info("> going to sleep")

  # make sure the rtc flags are cleared before going back to sleep
  logging.debug("  - clearing and disabling previous alarm")
  rtc.clear_timer_flag() # TODO this was removed from 0.0.8
  rtc.clear_alarm_flag()

  # set alarm to wake us up for next reading
  dt = rtc.datetime()
  hour, minute, second = dt[3:6]

  # calculate how many minutes into the day we are
  if time_override is not None:
    minute += time_override
  else:
    # if the time is very close to the end of the minute, advance to the next minute
    # this aims to fix the edge case where the board goes to sleep right as the RTC triggers, thus never waking up
    if second > 55:
      minute += 1
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
  logging.debug("  - on usb power (so can't shutdown). Halt and wait for alarm or user reset instead")
  board = get_board()
  while not rtc.read_alarm_flag():
    if hasattr(board, "check_trigger"):
      board.check_trigger()

    #time.sleep(0.25)

    if button_pin.value(): # allow button to force reset
      break

  logging.debug("  - reset")

  # reset the board
  machine.reset()
