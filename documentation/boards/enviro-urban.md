# Enviro Urban

A wireless outdoor air quality monitoring board with environmental and particulate sensors and a microphone.

Enviro Urban is an all in one board for checking up on all the airborne nasties that can occur in built up areas. There's a BME280 sensor for measuring temperature, humidity, and pressure, a microphone for noise monitoring and a pre-installed PMS5003I particulate sensor. Particulate matter is made up of tiny particles that are a mix of sizes and types, like dust, pollen, mould spores, smoke particles, organic particles and metal ions, and more. Particulates are much of what we think of as air pollution. 

## Readings

    "temperature": round(bme280_data[0], 2),
    "humidity": round(bme280_data[2], 2),
    "pressure": round(bme280_data[1] / 100.0, 2),
    "noise": round(noise_vpp, 2),
    "pm1": particulates(particulate_data, PM1_UGM3), 
    "pm2_5": particulates(particulate_data, PM2_5_UGM3), 
    "pm10": particulates(particulate_data, PM10_UGM3), 
  })




|Name|Parameter|Unit|Symbol|Example|
|---|---|---|---|---|
|Temperature|`temperature`|celcius|°C|`22.11`|
|Humidity|`humidity`|percent|%|`55.42`|
|Air Pressure|`pressure`|hectopascals|hPa|`997.16`|
|Noise|`noise`|voltage|V|`0.87`|
|PM1|`moisture_1`|micrograms per cubic metre|µg/m³|`9`|
|PM2.5|`moisture_2`|micrograms per cubic metre|µg/m³|`4`|
|PM10|`moisture_3`|micrograms per cubic metre|µg/m³|`2`|

## On-board devices

- BME280 temperature, pressure, humidity sensor. [View datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf)
- SPU0410HR5H MEMS microphone. [View datasheet](https://www.mouser.co.uk/datasheet/2/218/know_s_a0010769161_1-2271807.pdf)
- PMSA003I particulate matter sensor. [View datasheet](https://www.mouser.co.uk/datasheet/2/737/4505_PMSA003I_series_data_manual_English_V2_6-2490334.pdf)

## Power

Can be powered by a 2 x AAA battery pack, which fits neatly behind the board.

Any battery pack that can supply between 2V and 5.5V will work though - 2 or 3 alkaline AA or AAA cells, 4 rechargeable NiMH cells or a single cell LiPo.