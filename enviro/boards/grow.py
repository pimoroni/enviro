import time
from breakout_bme280 import BreakoutBME280
from breakout_ltr559 import BreakoutLTR559
from machine import Pin, PWM
from enviro import i2c
from phew import logging

CHANNEL_NAMES = ['A', 'B', 'C']

bme280 = BreakoutBME280(i2c, 0x77)
ltr559 = BreakoutLTR559(i2c)

piezo_pwm = PWM(Pin(28))

moisture_sensor_pins = [
  Pin(15, Pin.IN, Pin.PULL_DOWN),
  Pin(14, Pin.IN, Pin.PULL_DOWN),
  Pin(13, Pin.IN, Pin.PULL_DOWN)
]

pump_pins = [
  Pin(12, Pin.OUT, value=0),
  Pin(11, Pin.OUT, value=0),
  Pin(10, Pin.OUT, value=0)
]

def moisture_readings():
  results = []

  for i in range(0, 3):
    # count time for sensor to "tick" 25 times
    sensor = moisture_sensor_pins[i]

    last_value = sensor.value()
    start = time.ticks_ms()
    first = None
    last = None
    ticks = 0
    while ticks < 10 and time.ticks_diff(time.ticks_ms(), start) <= 1000:
      value = sensor.value()
      if last_value != value:
        if first == None:
          first = time.ticks_ms()
        last = time.ticks_ms()
        ticks += 1
        last_value = value

    if not first or not last:
      results.append(0.0)
      continue

    # calculate the average tick between transitions in ms
    average = time.ticks_diff(last, first) / ticks
    # scale the result to a 0...100 range where 0 is very dry
    # and 100 is standing in water
    #
    # dry = 10ms per transition, wet = 80ms per transition
    min_ms = 20
    max_ms = 80
    average = max(min_ms, min(max_ms, average)) # clamp range
    scaled = ((average - min_ms) / (max_ms - min_ms)) * 100
    results.append(round(scaled, 2))

  return results

# make a semi convincing drip noise
def drip_noise():
  piezo_pwm.duty_u16(32768)
  for i in range(0, 10):
      f = i * 20
      piezo_pwm.freq((f * f) + 1000)      
      time.sleep(0.02)
  piezo_pwm.duty_u16(0)

def water(moisture_levels):
  from enviro import config
  targets = [
    config.moisture_target_a, 
    config.moisture_target_b,
    config.moisture_target_c
  ]

  for i in range(0, 3):
    if moisture_levels[i] < targets[i]:
      # determine a duration to run the pump for
      duration = round((targets[i] - moisture_levels[i]) / 25, 1)

      logging.info(f"> sensor {CHANNEL_NAMES[i]} below moisture target {targets[i]} (currently at {int(moisture_levels[i])}).")

      if config.auto_water:
        logging.info(f"  - running pump {CHANNEL_NAMES[i]} for {duration} second(s)")
        pump_pins[i].value(1)
        time.sleep(duration)
        pump_pins[i].value(0)
      else:
        logging.info(f"  - playing beep")
        for j in range(0, i + 1):
          drip_noise()
        time.sleep(0.5)

def get_sensor_readings(seconds_since_last, is_usb_power):
  # bme280 returns the register contents immediately and then starts a new reading
  # we want the current reading so do a dummy read to discard register contents first
  bme280.read()
  time.sleep(0.1)
  bme280_data = bme280.read()

  ltr_data = ltr559.get_reading()

  moisture_levels = moisture_readings()

  water(moisture_levels) # run pumps if needed

  from ucollections import OrderedDict
  return OrderedDict({
    "temperature": round(bme280_data[0], 2),
    "humidity": round(bme280_data[2], 2),
    "pressure": round(bme280_data[1] / 100.0, 2),
    "luminance": round(ltr_data[BreakoutLTR559.LUX], 2),
    "moisture_a": round(moisture_levels[0], 2),
    "moisture_b": round(moisture_levels[1], 2),
    "moisture_c": round(moisture_levels[2], 2)
  })
  
def play_tone(frequency = None):
  if frequency:
    piezo_pwm.freq(frequency)
    piezo_pwm.duty_u16(32768)

def stop_tone():
  piezo_pwm.duty_u16(0)
