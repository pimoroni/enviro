# Troubleshooting your Enviro setup

Do not despair!

Setting up Enviro is a breeze if you get every answer right first time during provisioning but it's easy to get into a situation where something in your configuration isn't quite right and it can be hard to pin down exactly what it is.

## First things to try

Before we dig much deeper there are a few quick things to check:

### Try the provisioning process again

It's possible we just made an error entering our network details or nickname.

Press and hold the **POKE** button while briefly pressing **RESET**. Keep holding **POKE** until the **ACTIVITY** LED starts to blink quickly - this takes around five seconds.

Then follow the [provisioning guide](getting-started.md#provisioning) again to go through each step - this time your previous answers will already be filled in so it's ideal for reviewing everything to ensure there aren't any mistakes.

> *Note: your network password and the username and passwords for upload destinations are case sensitive - make sure you enter them perfectly!*

### Look at the `config.py` file

The provisioning process generates a file called `config.py` on your Enviro. If you manually edit this file, or it somehow becomes corrupted, it is possible that it will be unreadable by Enviro.

Try deleting `config.py` from your Enviro board and then pressing **RESET**. This will trigger the [provisioning process](getting-started.md#provisioning) to start again and you can configure your board from fresh.

### Inspect the logs

If you're happy the configuration is correct then it's worth taking a look in the log file to see if that reveals anything. Open `log.txt` and scroll to the bottom (new events are attached to the end of the file as they happen). Look specifically for lines that have the word `error` near the start.

The following errors have some common causes:

#### `! failed to connect to wireless network [network name]`

Enviro can't connect to your wireless network. This could be because the network name or password are wrong, or the device is too far away from the route to get a good signal.

Things to try:

- bring the board nearer your router to see if that helps.
- ask a friend, family member, or pet to double check the username and password are entered correctly
- reboot your router

#### `! low disk space`

If you allow Enviro to build up a lot of readings without uploading them or downloading them from the device manually then it is in danger of running out of space.

To mitigate this Enviro will actively delete old recordings, log files, and cache entries if it needs to causing you to lose data.

#### `! failed to synchronise clock`

Sometimes it may not be possible for Enviro to connect to the NTP server that provides it with time and date information.

You can normally ignore this error as it will only be a temporary issue and start working again without intervention. If it doesn't, double check your wi-fi details are correct.

#### `! failed to upload '[cache_file]'`

Enviro couldn't connect to your upload destination to transmit the readings it has stored.

If you're using Adafruit IO and this message also includes `Unprocessable Entity` then it usually means that you've run out of free feeds and need to upgrade to a paid plan. Adafruit IO offers 10 feeds for free.

### Upgrade your firmware

It's possible that you've encountered a bug that we've fixed in a newer version of the Enviro software so it's worth [upgrading the onboard software to the latest version.](https://github.com/pimoroni/enviro/blob/main/documentation/upgrading-firmware.md)
