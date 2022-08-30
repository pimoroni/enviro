import time
from breakout_bme280 import BreakoutBME280
from breakout_ltr559 import BreakoutLTR559
from machine import Pin, PWM
from enviro import i2c

bme280 = BreakoutBME280(i2c, 0x77)
ltr559 = BreakoutLTR559(i2c)

piezo_pwm = PWM(Pin(28))

moisture_sensor_pins = [
  Pin(15, Pin.IN, Pin.PULL_DOWN),
  Pin(14, Pin.IN, Pin.PULL_DOWN),
  Pin(13, Pin.IN, Pin.PULL_DOWN)
]

def sensors():
  return [
    "temperature",
    "humidity",
    "pressure",
    "light",
    "moisture_1",
    "moisture_2",
    "moisture_3"
  ]

def moisture_readings(sample_time_ms=500):  
  # get initial sensor state
  state = [sensor.value() for sensor in moisture_sensor_pins]

  # create an array for each sensor to log the times when the sensor state changed
  # then we can use those values to calculate an average tick time for each sensor
  changes = [[], [], []]
  
  start = time.ticks_ms()
  while time.ticks_ms() - start <= sample_time_ms:
    for i in range(0, len(state)):
      now = moisture_sensor_pins[i].value()
      if now != state[i]: # sensor output changed
        # record the time of the change and update the state
        changes[i].append(time.ticks_ms())
        state[i] = now

  # now we can average the readings for each sensor
  results = []
  for i in range(0, len(changes)):
    # if no sensor connected to change then we have no readings, skip
    if len(changes[i]) < 2:
      results.append(0)
      continue

    # calculate the average tick between transitions in ms
    average = (changes[i][-1] - changes[i][0]) / (len(changes[i]) - 1)

    # scale the result to a 0...100 range where 0 is very dry
    # and 100 is standing in water
    #
    # dry = 20ms per transition, wet = 60ms per transition
    scaled = (min(40, max(0, average - 20)) / 40) * 100
    results.append(scaled)

  return results

def get_sensor_readings():
  # bme280 returns the register contents immediately and then starts a new reading
  # we want the current reading so do a dummy read to discard register contents first
  bme280.read()
  time.sleep(0.1)
  bme280_data = bme280.read()

  ltr_data = ltr559.get_reading()

  moisture_data = moisture_readings(2000)

  return {
    "temperature": round(bme280_data[0], 2),
    "humidity": round(bme280_data[2], 2),
    "pressure": round(bme280_data[1] / 100.0, 2),
    "light": round(ltr_data[BreakoutLTR559.LUX], 2),
    "moisture_1": round(moisture_data[0], 2),
    "moisture_2": round(moisture_data[1], 2),
    "moisture_3": round(moisture_data[2], 2)
  }
  
def play_tone(frequency = None):
  if frequency:
    piezo_pwm.freq(frequency)
    piezo_pwm.duty_u16(32768)

def stop_tone():
  piezo_pwm.duty_u16(0)
