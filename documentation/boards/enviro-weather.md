# Enviro Weather

A wireless climate and environmental monitoring system designed to make hooking up weather sensors a breeze (or a squall, or a gale).

Enviro Weather is a super slimline all in one board for keeping a (weather) eye on the great outdoors. The onboard sensors can measure temperature, humidity, pressure and light. The sturdy RJ11 connectors (remember those?) will let you easily attach wind and rain sensors. We've designed this one to be installed outside in a suitable weatherproof enclosure (like a Stevenson screen) and connected to wirelessly - logging the data locally or piping it into databases, home automation dashboards or online citizen science projects.

## Readings

|Name|Parameter|Unit|Symbol|Example|
|---|---|---|---|---|
|Temperature|`temperature`|celcius|°C|`22.11`|
|Humidity|`humidity`|percent|%|`55.42`|
|Dew Point|`dewpoint`|celcius|°C|`12.21`|
|Air Pressure|`pressure`|hectopascals|hPa|`997.16`|
|Adjusted Sea Level Air Pressure|`sea_level_pressure`|hectopascals|hPa|`1014.06`|
|Luminance|`luminance`|lux|lx|`35`|
|Rainfall|`rain`|millimetres|mm|`1.674`|
|Rainfall Average Second|`rain_per_second`|millimetres per second|mm/s|`1.674`|
|Rainfall Average Hour|`rain_per_hour`|millimetres per hour|mm/h|`1.674`|
|Rainfall Today (local time)|`rain_today`|millimetres accumulated today|mm/s|`1.674`|
|Wind Direction|`wind_direction`|angle|°|`45`|
|Wind Speed|`wind_speed`|metres per second|m/s|`0.45`|
|Voltage|`voltage`|volts|V|`4.035`|

The rain today value is adjusted for DST in the UK by setting uk_bst = True in config.py
For static time zone offsets (not taking account of DST), modify the utc_offset value in config.py
The time zone offset value is ignored if uk_bst = True

## On-board devices

- BME280 temperature, pressure, humidity sensor. [View datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf)
- LTR-559 light and proximity sensor. [View datasheet](https://optoelectronics.liteon.com/upload/download/ds86-2013-0003/ltr-559als-01_ds_v1.pdf)
- RJ11 connectors for connecting wind and rain sensors

## Power

Can be powered by a 2 x AAA battery pack, which fits neatly behind the board.

Any battery pack that can supply between 2V and 5.5V will work though - 2 or 3 alkaline AA or AAA cells, 4 rechargeable NiMH cells or a single cell LiPo.
