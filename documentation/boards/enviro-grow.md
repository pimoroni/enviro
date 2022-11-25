# Enviro Grow

A wireless monitoring system to help take good care of your plants. Monitor moisture levels with the soil sensors, or hook up pumps to make a whole auto-watering system!

Enviro Grow comes with three capacitive moisture sensors to monitor up to three pots or trays of seeds separately. Because there are no exposed electrodes, capacitive sensors are a lot less vulnerable to corrosion over time than old school resistive sensors. There's also a buzzer so it can signal your attention. The onboard sensors can measure temperature, humidity, pressure and light so you can finetune the growing conditions for your plants (you could also use the light sensor it to stop the buzzer from going off at night).

## Readings

|Name|Parameter|Unit|Symbol|Example|
|---|---|---|---|---|
|Temperature|`temperature`|celcius|°C|`22.11`|
|Humidity|`humidity`|percent|%|`55.42`|
|Air Pressure|`pressure`|hectopascals|hPa|`997.16`|
|Luminance|`luminance`|lux|lx|`35`|
|Moisture Sensor A|`moisture_a`|percent|%|`17`|
|Moisture Sensor B|`moisture_b`|percent|%|`45`|
|Moisture Sensor C|`moisture_c`|percent|%|`76`|
|Voltage|`voltage`|volts|V|`4.035`|

## On-board devices

- BME280 temperature, pressure, humidity sensor. [View datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf)
- LTR-559 light and proximity sensor. [View datasheet](https://optoelectronics.liteon.com/upload/download/ds86-2013-0003/ltr-559als-01_ds_v1.pdf)
- 3x capacitive moisture sensors
- 3x low current drivers for pumps
- Piezo buzzer

## Power

Can be powered by a 2 x AAA battery pack, which fits neatly behind the board.

Any battery pack that can supply between 2V and 5.5V will work though - 2 or 3 alkaline AA or AAA cells, 4 rechargeable NiMH cells or a single cell LiPo.
