**New firmware release!** 

This is an alpha release of what will become the official Enviro firmware next week.

Key changes:

- Provisioning
  - much better performance, more snappy
  - no longer hangs in some setups
  - empty and duplicate network names hidden
  - better handling of config file writing
- Readings now synched to clock time rather than just relative to each other
- Battery voltage reported as a reading
- Poke button now works when plugged in via USB
- Boards all work properly when plugged into USB (previous had to use a battery)
- Enviro Weather 🌦️
  - rain sensor trigger fixed
  - improved wind speed readings at low wind speeds
- Enviro Indoor 🛋️
  - basic support for VOC sensor/air quality readings added
- Enviro Grow 🪴
  - auto watering / audio alert trigger support
  - moisture sensor readings corrected

There have also been many small bug fixes and improvements made - it is well worth upgrading!

Please try it if you have the chance and let us know how it goes! 

Download the firmware here: https://github.com/pimoroni/enviro/releases/tag/v0.0.8

---

# Enviro MicroPython firmware <!-- omit in toc -->

- [About Enviro](#about-enviro)
- [Powering Enviro boards](#powering-enviro-boards)
- [Supported products](#supported-products)
- [Supported endpoints](#supported-endpoints)
- [Documentation](#documentation)

## About Enviro

Our Enviro range of boards offer a wide array of environmental sensing and data logging functionality. They are designed to be setup in location for months at a time and take regular measurements.

On top of their individual features the boards all share a common set of functions:

- on-board Pico W with RP2040 MCU and WiFi functionality
- accurate real-time clock (RTC) to maintain the time between boots
- a collection of wake event triggers (user button, RTC, external trigger)
- battery power input suitable for 1.8-5.5V input (ideal for 2x or 3x alkaline/NiMH cells or a single cell LiPo)
- reset button for frictionless debugging
- user button to trigger wake events or enter provisioning mode
- activity and warn LEDs to show current status
- Qw/ST connector to allow you to customise your sensor suite

These common features mean that the modules can run off very little power for long periods of time. During sleep (when the RTC remains active) the boards only consume a few microamps of power meaning they can last for months on a small battery pack. The modules wake up at regular intervals (or on a fixed schedule) to take a reading, store it, and go back to sleep.

As well as logging data locally Enviro boards can also use the Pico W's wireless functionality to upload the data they capture to a [supported endpoint](#supported-endpoints). Wireless communications take a lot of power so this should be done as infrequently as possible.

## Powering Enviro boards

Enviro boards are designed to run for months on a set of batteries so that you can install them wherever they can gather the best data - perhaps on that high shelf in the corner of the kitchen that you can't quite reach, under a Stevenson screen in the back garden, or tucked in the shed.

You can use 3xAA or 3xAAA (either alkaline or NiMH), a single cell LiPo battery, or a USB cable to power Enviro boards.

## Supported products

- Enviro Indoor ([store link](https://shop.pimoroni.com/products/enviro-indoor))
- Enviro Grow ([store link](https://shop.pimoroni.com/products/enviro-grow))
- Enviro Weather ([store link](https://shop.pimoroni.com/products/enviro-weather))
- Enviro Urban ([store link](https://shop.pimoroni.com/products/enviro-urban))
- Enviro Camera ([store link](https://shop.pimoroni.com/products/enviro-camera)) - coming soon!

## Supported endpoints
- [Adafruit IO](documentation/destinations/adafruit-io.md)
- [InfluxDB](documentation/destinations/influxdb.md)
- [MQTT](documentation/destinations/mqtt.md)
- [Custom HTTP endpoint](documentation/destinations/custom-http-endpoint.md)

## Documentation

- Getting Started with Enviro ([Learn link](https://learn.pimoroni.com/article/getting-started-with-enviro))
- [Quickstart guide](documentation/getting-started.md)
- [Troubleshooting your Enviro board](documentation/troubleshooting.md)
- [Upgrading firmware](documentation/upgrading-firmware.md)
- Sensor info: [Indoor](documentation/boards/enviro-indoor.md) / [Grow](documentation/boards/enviro-grow.md) / [Weather](documentation/boards/enviro-weather.md) / [Urban](documentation/boards/enviro-urban.md)
