import time

import breakout_scd41

def get_readings(i2c, address, seconds_since_last):
  breakout_scd41.init(i2c)
  breakout_scd41.start()

  retries = 25
  while retries > 0 and not breakout_scd41.ready():
    time.sleep(0.2)
    retries -= 1

  if retries == 0:
    return {}

  scd_co2, scd_temp, scd_humidity = breakout_scd41.measure()

  from ucollections import OrderedDict
  return OrderedDict({
    "scd_co2": scd_co2,
    "scd_temperature": scd_temp,
    "scd_humidity": scd_humidity
  })