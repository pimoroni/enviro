# enviro - wireless environmental monitoring and logging
#
# on first run enviro will go into provisioning mode where it appears
# as a wireless access point called "Enviro <board type> Setup". connect
# to the access point with your phone, tablet or laptop and follow the
# on screen instructions.
#
# the provisioning process will generate a `config.py` file which 
# contains settings like your wifi username/password, how often you
# want to log data, and where to upload your data once it is collected.
#
# you can use enviro out of the box with the options that we supply
# or alternatively you can create your own firmware that behaves how
# you want it to - please share your setups with us! :-)
#
# need help? check out https://pimoroni.com/enviro-guide
#
# happy data hoarding,
#
#   - the Pimoroni Pirate Crew

import enviro
from enviro import logging
import time, os, urequests



# initialise 
enviro.startup()


# if button held for 3 seconds on startup then go into provisioning mode
user_requested_provisioning = enviro.button_held_for(3)


# if enviro isn't configured or the user requested provisioning then
# put the board into provisioning (setup) mode
if user_requested_provisioning or enviro.needs_provisioning():
  logging.info("> entering provisioning mode")
  enviro.provision()
  # control never returns to here, provisioning takes over comp letely


# import config now that we know provisioning isn't needed
import config


# if the clock isn't set then we need to fetch the time from an NTP
# server. this requires connecting to WiFi
if not enviro.clock_set():
  logging.info("> clock not set, synchronise from ntp server")
  if not enviro.sync_clock_from_ntp():    
    # if we failed to synchronise the clock then turn on the warning
    # led and go back to sleep for another cycle
    logging.warn(">  failed to sync clock")
    warn_led(WARN_LED_BLINK)
    enviro.sleep(config.reading_frequency)


if enviro.low_disk_space():
  # there is less than 10% of the filesystem available, this probably
  # means that cached results are not getting uploaded and cleared so
  # warn the user and go back to sleep
  logging.warn(">  low disk space")
  warn_led(WARN_LED_BLINK)
  enviro.sleep(config.reading_frequency)


# take a reading from the sensors
reading = enviro.get_sensor_readings()


# save the reading into the local reading files (look in "/readings")
enviro.save_reading(reading)


# if we have a destination to send our readings to then also cache it
# until our next scheduled upload
if config.destination:
  enviro.cache_upload(reading)


# check if we've reached the time to upload our cached data
cache_file_count = enviro.cached_upload_count()
if cache_file_count >= config.upload_frequency:
  logging.info(f"> {cache_file_count} cache files need uploading")

  enviro.upload_readings()

enviro.sleep(config.reading_frequency)