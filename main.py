# Enviro - wireless environmental monitoring and logging
#
# On first run Enviro will go into provisioning mode where it appears
# as a wireless access point called "Enviro <board type> Setup". Connect
# to the access point with your phone, tablet or laptop and follow the
# on screen instructions.
#
# The provisioning process will generate a `config.py` file which 
# contains settings like your wifi username/password, how often you
# want to log data, and where to upload your data once it is collected.
#
# You can use enviro out of the box with the options that we supply
# or alternatively you can create your own firmware that behaves how
# you want it to - please share your setups with us! :-)
#
# Need help? check out https://pimoroni.com/enviro-guide
#
# Happy data hoarding folks,
#
#   - the Pimoroni pirate crew

# import enviro firmware, this will trigger provisioning if needed

import enviro
import os, time

post_time = time.ticks_ms()

from phew import logging
logging.debug(f"Tms (post enviro) = {post_time}")

# initialise enviro
enviro.startup()

logging.debug(f"Tms (post startup) = {time.ticks_ms()}")

# if the clock isn't set...
if not enviro.is_clock_set():
  logging.info("> clock not set, synchronise from ntp server")
  if not enviro.sync_clock_from_ntp():
    # failed to talk to ntp server go back to sleep for another cycle
    enviro.halt("! failed to synchronise clock")  

# check disk space...
if enviro.low_disk_space():
  # less than 10% of diskspace left, this probably means cached results
  # are not getting uploaded so warn the user and halt with an error
  enviro.halt("! low disk space")

# TODO this seems to be useful to keep around?
filesystem_stats = os.statvfs(".")
logging.debug(f"> {filesystem_stats[3]} blocks free out of {filesystem_stats[2]}")

# TODO should the board auto take a reading when the timer has been set, or wait for the time?
# take a reading from the onboard sensors
logging.debug(f"> taking new reading")
reading = enviro.get_sensor_readings()

# here you can customise the sensor readings by adding extra information
# or removing readings that you don't want, for example:
# 
#   del readings["temperature"]        # remove the temperature reading
#
#   readings["custom"] = my_reading()  # add my custom reading value

# is an upload destination set?
if enviro.config.destination:
  # if so cache this reading for upload later
  logging.debug(f"> caching reading for upload")
  enviro.cache_upload(reading)

  # if we have enough cached uploads...
  if enviro.is_upload_needed():
    logging.info(f"> {enviro.cached_upload_count()} cache file(s) need uploading")
    enviro.upload_readings()
  else:
    logging.info(f"> {enviro.cached_upload_count()} cache file(s) not being uploaded. Waiting until there are {enviro.config.upload_frequency} file(s)")
else:
  # otherwise save reading to local csv file (look in "/readings")
  logging.debug(f"> saving reading locally")
  enviro.save_reading(reading)

# go to sleep until our next scheduled reading
enviro.sleep()