# Enviro Urban

A wireless outdoor air quality monitoring board with environmental and particulate sensors and a microphone.

Enviro Urban is an all in one board for checking up on all the airborne nasties that can occur in built up areas. There's a BME280 sensor for measuring temperature, humidity, and pressure, a microphone for noise monitoring and a pre-installed PMS5003I particulate sensor. Particulate matter is made up of tiny particles that are a mix of sizes and types, like dust, pollen, mould spores, smoke particles, organic particles and metal ions, and more. Particulates are much of what we think of as air pollution. 

## Readings

|Name|Parameter|Unit|Symbol|Example|
|---|---|---|---|---|
|Temperature|`temperature`|celcius|°C|`22.11`|
|Humidity|`humidity`|percent|%|`55.42`|
|Air Pressure|`pressure`|hectopascals|hPa|`997.16`|
|Noise|`noise`|voltage|V|`0.87`|
|PM1|`pm1`|micrograms per cubic metre|µg/m³|`9`|
|PM2.5|`pm2_5`|micrograms per cubic metre|µg/m³|`4`|
|PM10|`pm10`|micrograms per cubic metre|µg/m³|`2`|
|Voltage|`voltage`|volts|V|`4.035`|

## On-board devices

- BME280 temperature, pressure, humidity sensor. [View datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf)
- SPU0410HR5H MEMS microphone. [View datasheet](https://www.mouser.co.uk/datasheet/2/218/know_s_a0010769161_1-2271807.pdf)
- PMSA003I particulate matter sensor. [View datasheet](https://www.mouser.co.uk/datasheet/2/737/4505_PMSA003I_series_data_manual_English_V2_6-2490334.pdf)

## Power

Can be powered by a 3 x AA battery pack, which fits neatly behind the board.

Any battery pack that can supply between 2V and 5.5V will work though - 2 or 3 alkaline AA or AAA cells, 4 rechargeable NiMH cells or a single cell LiPo.
