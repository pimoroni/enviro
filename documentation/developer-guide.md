
## Tips if you want to modify the code
### Adding data points to the returned readings
#### Simple data mangling
You can customise the sensor readings to be saved and uploaded by adjusting the "reading" dictionary; Adding extra information or removing data points that you don't want. Make any adustments after the line populating the reading dictionary:
```
reading = enviro.get_sensor_readings()
```

For example:
```
reading = enviro.get_sensor_readings()

del reading["temperature"]        # remove the temperature data
reading["custom"] = my_reading()  # add my custom reading value
```

#### Custom data points (BME688 example)
Add simple built in module calls in main.py after the reading dictionary is populated and modify the reading dictionary as required

Add your code after the line:
```
reading = enviro.get_sensor_readings()
```

A simple BME688 module example:
```
reading = enviro.get_sensor_readings()

from breakout_bme68x import BreakoutBME68X
bme = BreakoutBME68X(enviro.i2c)
temperature, pressure, humidity, gas_resistance, status, gas_index, meas_index = bme.read()
reading["temperature2"] = temperature
```
Credit: @hfg-gmuend in [#178](https://github.com/pimoroni/enviro/issues/178)
  
The above code will overwrite the returned data if you use the same key name e.g. "temperature", ensure this is what you want to do, or otherwise pick a unique name for your new data point e.g. "temperature2"

#### Modifying specific board sensor collections
If the existing readings from a specific board require adjustment, for example adding a sea level adjusted value for atmospheric pressure readings. This should be done in the in board specific file in the boards directory, modifying the necessary lines in the get_sensor_readings() function.

### Code structure

### Boot up process

The Enviro boot up process is relatively complex as we need to ensure that things like the real time clock are synchronised and our wireless connection is functional before we attempt to take any readings.

```mermaid
  graph TD;
    provision[Enter provisioning mode]
    check_rtc{Is RTC<br>synched?}
    button_held{User requested<br>provisioning?}
    take_reading[Take sensor readings]
    set_rtc_from_ntp[Initialise RTC]
    connect_to_wifi_for_rtc[Connect to WiFi]
    connect_to_wifi_for_upload[Connect to WiFi]
    check_disk_space[Disk space OK?]
    save_reading[Save sensor readings]
    cache_for_upload[Cache reading for upload later]
    have_destination[Is an upload destination configured?]
    upload_cached_readings[Upload cached readings]
    need_uploading[Is the upload cache full?]
    sleep[Go to sleep]
    sleep2[Go to sleep]
    sleep3[Go to sleep]
    is_provisioned{Is provisioned?}
    wake[Wake]
    warning1[Turn on warning LED and sleep]
    warning2[Turn on warning LED and sleep]
    warning3[Turn on warning LED and sleep]

    wake-->button_held

    button_held-->|No|is_provisioned
    button_held-->|Yes|provision

    is_provisioned-->|Yes|check_rtc
    is_provisioned-->|No|provision

    check_rtc-->|Yes|check_disk_space
    check_rtc-->|No|connect_to_wifi_for_rtc

    connect_to_wifi_for_rtc-->|Yes|set_rtc_from_ntp-->check_disk_space
    connect_to_wifi_for_rtc-->|No|warning1

    check_disk_space-->|OK|take_reading
    check_disk_space-->|Low|warning2

    take_reading-->save_reading-->have_destination

    have_destination-->|Yes|cache_for_upload-->need_uploading

    need_uploading-->|Yes|connect_to_wifi_for_upload

    connect_to_wifi_for_upload-->|Yes|upload_cached_readings-->sleep2
    connect_to_wifi_for_upload-->|No|warning3

    need_uploading-->|No|sleep

    have_destination-->|No|sleep3

```
