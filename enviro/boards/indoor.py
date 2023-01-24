import enviro.helpers as helpers
import math
from breakout_bme68x import BreakoutBME68X
from breakout_bh1745 import BreakoutBH1745

from enviro import config
from enviro import i2c

bme688 = BreakoutBME68X(i2c, address=0x77)

bh1745 = BreakoutBH1745(i2c)
# need to write default values back into bh1745 chip otherwise it
# reports bad results (this is undocumented...)
i2c.writeto_mem(0x38, 0x44, b'\x02')

def lux_from_rgbc(r, g, b, c):
  if g < 1:
      tmp = 0
  elif (c / g < 0.160):
      tmp = 0.202 * r + 0.766 * g
  else:
      tmp = 0.159 * r + 0.646 * g
  tmp = 0 if tmp < 0 else tmp
  integration_time = 160
  gain = 1
  return round(tmp / gain / integration_time * 160)

def colour_temperature_from_rgbc(r, g, b, c):
  if (g < 1) or (r + g + b < 1):
      return 0
  r_ratio = r / (r + g + b)
  b_ratio = b / (r + g + b)
  e = 2.71828
  ct = 0
  if c / g < 0.160:
      b_eff = min(b_ratio * 3.13, 1)
      ct = ((1 - b_eff) * 12746 * (e ** (-2.911 * r_ratio))) + (b_eff * 1637 * (e ** (4.865 * b_ratio)))
  else:
      b_eff = min(b_ratio * 10.67, 1)
      ct = ((1 - b_eff) * 16234 * (e ** (-2.781 * r_ratio))) + (b_eff * 1882 * (e ** (4.448 * b_ratio)))
  if ct > 10000:
      ct = 10000
  return round(ct)

def get_sensor_readings(seconds_since_last, is_usb_power):
  data = bme688.read()

  temperature = round(data[0], 2)
  humidity = round(data[2], 2)

  # Compensate for additional heating when on usb power - this also changes the
  # relative humidity value.
  if is_usb_power:
    adjusted_temperature = temperature - config.usb_power_temperature_offset
    absolute_humidity = helpers.relative_to_absolute_humidity(humidity, temperature)
    humidity = helpers.absolute_to_relative_humidity(absolute_humidity, adjusted_temperature)
    temperature = adjusted_temperature

  pressure = round(data[1] / 100.0, 2)
  gas_resistance = round(data[3])
  # an approximate air quality calculation that accounts for the effect of
  # humidity on the gas sensor
  # https://forums.pimoroni.com/t/bme680-observed-gas-ohms-readings/6608/25
  aqi = round(math.log(gas_resistance) + 0.04 * humidity, 1)

  bh1745.measurement_time_ms(160)
  r, g, b, c = bh1745.rgbc_raw()

  from ucollections import OrderedDict
  return OrderedDict({
    "temperature": temperature,
    "humidity": humidity,
    "pressure": pressure,
    "gas_resistance": gas_resistance,
    "aqi": aqi,
    "luminance": lux_from_rgbc(r, g, b, c),
    "color_temperature": colour_temperature_from_rgbc(r, g, b, c)
  })
