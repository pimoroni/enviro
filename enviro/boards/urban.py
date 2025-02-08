# imports common to all boards
from enviro import config
import enviro.helpers as helpers
from enviro import i2c
from ucollections import OrderedDict

# board specific imports
import time
from machine import Pin, ADC
from breakout_bme280 import BreakoutBME280
from pimoroni_i2c import PimoroniI2C
from phew import logging

# board specific global constants
# how long to capture the microphone signal for when taking a reading, in milliseconds
MIC_SAMPLE_TIME_MS = 500

# board specific sensors
bme280 = BreakoutBME280(i2c, 0x77)
noise_adc = ADC(0)

# board specific pins
sensor_reset_pin = Pin(9, Pin.OUT, value=True)
sensor_enable_pin = Pin(10, Pin.OUT, value=False)
boost_enable_pin = Pin(11, Pin.OUT, value=False)
PM1_UGM3                = 2
PM2_5_UGM3              = 3
PM10_UGM3               = 4
PM1_UGM3_ATHMOSPHERIC   = 5
PM2_5_UGM3_ATHMOSPHERIC = 6
PM10_UGM3_ATHMOSPHERIC  = 7
PM0_3_PER_LITRE         = 8
PM0_5_PER_LITRE         = 9
PM1_PER_LITRE           = 10
PM2_5_PER_LITRE         = 11
PM5_PER_LITRE           = 12
PM10_PER_LITRE          = 13

# define functions
def particulates(particulate_data, measure):
  # bit of a fudge to convert decilitres into litres... who uses decilitre?!
  multiplier = 10 if measure >= PM0_3_PER_LITRE else 1
  return ((particulate_data[measure * 2] << 8) | particulate_data[measure * 2 + 1]) * multiplier

def get_sensor_readings(seconds_since_last, is_usb_power):
  # bme280 returns the register contents immediately and then starts a new reading
  # we want the current reading so do a dummy read to discard register contents first
  bme280.read()
  time.sleep(0.1)
  bme280_data = bme280.read()

  temperature = round(bme280_data[0], 2)
  pressure = round(bme280_data[1] / 100.0, 2)
  humidity = round(bme280_data[2], 2)
  
  # Compensate for additional heating when on usb power - this also changes the
  # relative humidity value.
  if is_usb_power:
    adjusted_temperature = temperature - config.usb_power_temperature_offset
    absolute_humidity = helpers.relative_to_absolute_humidity(humidity, temperature)
    humidity = helpers.absolute_to_relative_humidity(absolute_humidity, adjusted_temperature)
    temperature = adjusted_temperature
    
  logging.debug("  - starting sensor")
  boost_enable_pin.value(True)
  sensor_enable_pin.value(True)
  logging.debug("  - wait 5 seconds for airflow")
  time.sleep(5) # allow airflow to start

  # setup the i2c bus for the particulate sensor
  logging.debug("  - taking pms5003i reading")
  pms_i2c = PimoroniI2C(14, 15, 100000)
  particulate_data = pms_i2c.readfrom_mem(0x12, 0x00, 32)
  pm1 = particulates(particulate_data, PM1_UGM3)
  pm2_5 = particulates(particulate_data, PM2_5_UGM3) 
  pm10 = particulates(particulate_data, PM10_UGM3)

  sensor_enable_pin.value(False)
  boost_enable_pin.value(False)

  logging.debug("  - taking microphone reading")
  start = time.ticks_ms()
  min_value = 1.65
  max_value = 1.65
  while time.ticks_diff(time.ticks_ms(), start) < MIC_SAMPLE_TIME_MS:
    value = (noise_adc.read_u16() * 3.3) / 65535
    min_value = min(min_value, value)
    max_value = max(max_value, value)
  
  noise_vpp = max_value - min_value
  noise = round(noise_vpp, 3)


  return OrderedDict({
    "temperature": temperature,
    "humidity": humidity,
    "pressure": pressure,
    "noise": noise,
    "pm1": pm1, 
    "pm2_5": pm2_5, 
    "pm10": pm10
  })
