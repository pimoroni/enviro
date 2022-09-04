# Enviro Indoor

A wireless environmental monitoring board to keep track of inside conditions in your home, office or other habitat. Onboard sensors can measure temperature, humidity, pressure, gas and light.

The top of the range BME688 sensor on Enviro Indoor can measure temperature/humidity/pressure with a high degree of precision, and the gas scanner will react to changes in volatile organic compounds (VOCs), volatile sulfur compounds (VSCs) and the presence of carbon monoxide and hydrogen to give a general measure of air quality. The BH1745 light sensor can tell you the luminance and colour of light, so you could use it to detect unrestful blue light or adjust your lighting's intensity/hue depending on the time of day.

## Readings

|Name|Parameter|Unit|Symbol|Example|
|---|---|---|---|---|
|Temperature|`temperature`|celcius|°C|`22.11`|
|Humidity|`humidity`|percent|%|`55.42`|
|Air Pressure|`pressure`|hectopascals|hPa|`997.16`|
|Gas Resistance|`gas_resistance`|ohms|Ω|`36551`|
|Air Quality Index|`aqi`|percent|%|`13.1`|
|Luminance|`luminance`|lux|lx|`35`|
|Color Temperature|`color_temperature`|kelvin|K|`4581`|
|Voltage|`voltage`|volts|V|`4.035`|

## On-board devices

- BME688 4-in-1 temperature, pressure, humidity and gas sensor. [View datasheet](https://cdn.shopify.com/s/files/1/0174/1800/files/bst-bme688-ds000.pdf?v=1620834794)
- BH1745 light (luminance and colour) sensor. [View datasheet](https://www.mouser.co.uk/datasheet/2/348/bh1745nuc-e-519994.pdf)

## Power

Can be powered by a 2 x AAA battery pack, which fits neatly behind the board.

Any battery pack that can supply between 2V and 5.5V will work though - 2 or 3 alkaline AA or AAA cells, 4 rechargeable NiMH cells or a single cell LiPo.