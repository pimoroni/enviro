from phew import logging as logging
import time
import breakout_scd41

# CO2 Sensor
# https://shop.pimoroni.com/products/scd41-co2-sensor-breakout
# https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/breakout_scd41

from enviro.board import i2c

breakout_scd41.init(i2c)

def qtsensors():
    return [
        "scd41_co2",
        "scd41_temperature",
        "scd41_humidity"
    ]

def get_qtsensor_readings():
    breakout_scd41.start()
    while breakout_scd41.ready() is False:
        logging.info("CO2 sensor not ready, sleeping 5s")
        time.sleep(5)
    scd41_co2, scd41_temperature, scd41_relative_humidity = breakout_scd41.measure()
    breakout_scd41.stop()
    return {"scd41_co2": scd41_co2, "scd41_temperature": scd41_temperature, "scd41_humidity": scd41_relative_humidity}
