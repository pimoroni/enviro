# Enviro MicroPython firmware

Our Enviro range of boards offer a wide array of environmental sensing and data logging functionality. They are designed to be setup in location for months at a time and take regular measurements.

- [Getting started guide](documentation/getting-started.md)
- [Troubleshooting your Enviro board](documentation/troubleshooting.md)
- [Upgrading firmware](documentation/upgrading-firmware.md)

## About Enviro

On top of their individual features the boards all share a common set of functionality:

- on-board PicoW with RP2040 MCU and WiFi functionality
- accurate real-time clock (RTC) to maintain the time between boots
- a collection of wake event triggers (user button, RTC, external trigger)
- battery power input suitable for 1.8-5.5V input (ideal for 2x or 3x alkaline/NiMH cells or a single cell LiPo)
- reset button for frictionless debugging
- user button to trigger wake events or enter provisioning mode
- activity and warn LEDs to show current status
- Qw/ST connector to allow you to customise your sensor suite

These common features are mostly aimed at ensuring the modules can run off very little power for long periods of time. During sleep (when the RTC remains active) the boards only consume a few microamps of power meaning they can last for months on a small battery pack. The modules wake up at regular intervals (or on a fixed schedule) to take a reading, store it, and go back to sleep.

As well as logging data locally the modules can also (if they have access to a wireless network) upload the data they capture to a service like Adafruit.io. Wireless communications takes a lot of power so this should be done as infrequently as possible.

## Powering Enviro boards

Enviro boards are designed to run for months on a set of batteries so that you can install them wherever they can gather the best data - perhaps on that high shelf in the corner of the kitchen that you can't quite reach, under a Stevenson screen in the back garden, or tucked in the shed.

You can use 3xAA or 3xAAA (either alkaline or NiMH), a single cell LiPo battery, or a USB cable to power Enviro boards.
