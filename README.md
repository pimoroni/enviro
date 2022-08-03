# Enviro MicroPython firmware

Our Enviro range of boards offer a wide array of environmental sensing and data logging functionality. They are designed to be setup in location for months at a time and take regular measurements.

On top of their individual features the boards all share a common set of functionality:

- on-board PicoW with RP2040 MCU and WiFi functionality
- accurate real-time clock (RTC) to maintain the time between boots
- a collection of wake event triggers (user button, RTC, external trigger)
- battery power input suitable for 1.8-5.5V input (ideal for 2x or 3x alkaline/NiMH cells or a single cell LiPo)
- reset button for frictionless debugging
- user button to trigger wake events or enter provisioning mode
- activity and warn LEDs to show current status
- Qw/ST connector to allow you to customise your sensor suite

These common features are mostly aimed at ensuring the modules can run off very little power for long periods of time. During sleep (when the RTC remains active) the boards only consume a few microamps of power meaning they can last for months on a small battery pack. The modules wake up at regular intervales (or on a fixed schedule) to take a reading, store it, and go back to sleep.

As well as logging data locally the modules can also (if they have access to a wireless network) upload the data they capture to a service like Adafruit.io. Wireless communications takes a lot of power so this should be done as infrequently as possible.

## Provisioning

On first boot you must provision your module. You may optionally supply a wireless network SSID and password for uploading data and select the type of module.

## Boot up process
```mermaid
  graph TD;
    provision[Enter provisioning mode]
    check_rtc{Is RTC<br>synched?}
    wake_reason[Determine wake reason]
    button_held{Held for<br>3 seconds?}
    take_reading[Take sensor readings]
    set_rtc_from_ntp[Initialise RTC<br>from pool.ntp.org]
    log_readings[Log sensor readings]
    should_upload{Do readings<br>need uploading?}
    upload_readings[Upload sensor readings]
    sleep[Go to sleep]
    is_provisioned{Is provisioned?}
    read_secrets[Read secrets]
    wake[Wake]

    wake-->read_secrets-->is_provisioned

    is_provisioned-->|No|provision
    is_provisioned-->|Yes|wake_reason

    wake_reason-->|RTC Alarm|check_rtc
    wake_reason-->|Button press|button_held
    wake_reason-->|External Trigger|check_rtc

    button_held-->|No|check_rtc
    button_held-->|Yes|provision

    check_rtc-->|No|set_rtc_from_ntp-->take_reading
    check_rtc-->|Yes|take_reading

    take_reading-->log_readings

    log_readings-->should_upload

    should_upload-->|No|sleep
    should_upload-->|Yes|upload_readings-->sleep


```
