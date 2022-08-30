import time, math
from breakout_bme280 import BreakoutBME280
from breakout_ltr559 import BreakoutLTR559
from machine import Pin, PWM
from pimoroni import Analog
from enviro import i2c

bme280 = BreakoutBME280(i2c, 0x77)
ltr559 = BreakoutLTR559(i2c)

piezo_pwm = PWM(Pin(28))

wind_direction_pin = Analog(26)
wind_speed_pin = Pin(9, Pin.IN, Pin.PULL_UP)
rain_pin = Pin(10, Pin.IN, Pin.PULL_DOWN)

def sensors():
  return [
    "temperature",
    "humidity",
    "pressure",
    "light",
    "wind_speed",
    "rain",
    "wind_direction"
  ]

def wind_speed(sample_time_ms=500):  
  # get initial sensor state
  state = wind_speed_pin.value()

  # create an array for each sensor to log the times when the sensor state changed
  # then we can use those values to calculate an average tick time for each sensor
  ticks = []
  
  start = time.ticks_ms()
  while time.ticks_ms() - start <= sample_time_ms:
    now = wind_speed_pin.value()
    if now != state: # sensor output changed
      # record the time of the change and update the state
      ticks.append(time.ticks_ms())
      state = now

  # if no sensor connected then we have no readings, skip
  if len(ticks) < 2:
    return 0

  # calculate the average tick between transitions in ms
  average_tick_ms = (ticks[-1] - ticks[0]) / (len(ticks) - 1)

  # work out rotation speed in hz (two ticks per rotation)
  rotation_hz = (1000 / average_tick_ms) / 2

  # calculate the wind speed in metres per second
  radius = 7.0
  circumference = radius * 2.0 * math.pi
  factor = 0.0218  # scaling factor for wind speed in m/s
  wind_m_s = rotation_hz * circumference * factor

  return wind_m_s

def wind_direction():
  # adc reading voltage to cardinal direction taken from our python
  # library - each array index represents a 45 degree step around
  # the compass (index 0 == 0, 1 == 45, 2 == 90, etc.)
  # we find the closest matching value in the array and use the index
  # to determine the heading
  ADC_TO_DEGREES = (0.9, 2.0, 3.0, 2.8, 2.5, 1.5, 0.3, 0.6)

  closest_index = -1
  last_index = None

  # ensure we have two readings that match in a row as otherwise if
  # you read during transition between two values it can glitch
  # fixes https://github.com/pimoroni/enviro/issues/20
  while True:
    value = wind_direction_pin.read_voltage()

    closest_index = -1
    closest_value = float('inf')

    for i in range(8):
      distance = abs(ADC_TO_DEGREES[i] - value)
      if distance < closest_value:
        closest_value = distance
        closest_index = i

    if last_index == closest_index:
      break
      
    last_index = closest_index

  return closest_index * 45

def get_sensor_readings():
  # bme280 returns the register contents immediately and then starts a new reading
  # we want the current reading so do a dummy read to discard register contents first
  bme280.read()
  time.sleep(0.1)
  bme280_data = bme280.read()

  ltr_data = ltr559.get_reading()

  return {
    "temperature": round(bme280_data[0], 2),
    "humidity": round(bme280_data[2], 2),
    "pressure": round(bme280_data[1] / 100.0, 2),
    "light": round(ltr_data[BreakoutLTR559.LUX], 2),
    "wind_speed": wind_speed(),
    "rain": 0, #
    "wind_direction": wind_direction()
  }
  