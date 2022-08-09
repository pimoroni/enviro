# Getting started with Enviro <!-- omit in toc -->

- [Board Overview](#board-overview)
- [Provisioning your board](#provisioning-your-board)
  - [Powering up for the first time](#powering-up-for-the-first-time)
  - [Provisioning](#provisioning)
  - [Choosing a nickname](#choosing-a-nickname)
  - [Wireless network details](#wireless-network-details)
  - [Reading frequency](#reading-frequency)
  - [Upload frequency](#upload-frequency)
  - [Upload destination](#upload-destination)
    - [Adafruit IO](#adafruit-io)
    - [MQTT](#mqtt)
    - [Custom HTTP endpoint](#custom-http-endpoint)
  - [That's all folks!](#thats-all-folks)

## Board Overview

Many features are common to all versions of Enviro - these provide the base functionality of deep sleep, user interaction, powering the board, and attaching accessories.

It's a good idea to familiarise yourself with where the buttons and indicators are before you start setting up your board:

![Features on the Enviro boards](images/board-features.png)

1. **POKE** button: wakes the board from sleep to take an immediate reading
2. **ACTIVITY** LED (white): pulses gently when the board is awake
3. **WARNING** LED (red): blinks if an error occurs (e.g. wireless connection is down)
4. Qw/ST connector: a convenient way to add extra sensors
5. Sensors: the collection of sensors that the board gathers data from (these vary depending on board type)
6. **RESET** button: resets the board
7. Battery connector: compatible with many battery holders and cells
8. USB connector: for accessing readings files and logs from your computer

---

## Provisioning your board

When you receive your Enviro board it will come preloaded with our software but will not be configured yet. You need to go through the provisioning process to tell it how to connect to your wireless network, when to take readings, and optionally where to upload them.

Follow these instructions to get your Enviro board configured and running:

### Powering up for the first time

Plug in your battery or USB cable and press the **POKE** button on the front of the board to wake it up. The **ACTIVITY** LED will turn on and then after about a second will start to pulse to show that it is working.

If you haven't already configured this board then it will automatically switch into provisioning (setup) mode - you can tell this has happened if the **ACTIVITY** LED starts to blink rapidly.

### Provisioning

From your phone, tablet, or computer go into settings and view the available wireless networks - there will be a new network visible called "**Enviro [Model] Setup**" (e.g. "Enviro Indoor Setup"). Connect to this network.

It may take a moment but the setup process should automatically pop up with an introduction screen showing the details of the board you're provisioning.

Click **Ready? Let's go! ➔** to start configuring your device.

### Choosing a nickname

To make managing multiple Enviro boards easier it's a good idea to give each board a sensible nickname so that you can easily identify and filter the readings it generates when uploaded to one of the endpoints we support.

The nickname can be anything you want but may only consist of lowercase letters (a-z), numbers (0-9), and the hyphen (-) symbol. Try to choose a name that identifies the purpose of this Enviro board (for example "main-bedroom", or "weather-station").

Click **Wireless setup ➔** to continue.

### Wireless network details

Enviro needs a network connection to upload your readings and synchronise its onboard clock.

A list of nearby wireless networks will be shown.

> Your network not showing? Click **Try scanning again** to refresh the list or move closer to your network router.

Select your network and enter your wireless password.

If, in the future, your board cannot see the wireless network when it needs to set its clock or upload data then it will blink the **WARN** LED to indicate that there is a problem.

Click **Logging ➔** to continue.

### Reading frequency

When it comes to choosing how often to take readings it can be tempting to think "more data is better!" but that will, of course, impact on the length of time your batteries last.

In between taking and uploading readings Enviro spends most of its time in a deep sleep which consumes very little power - it can stay in this state for years on just a couple of AA batteries!

Each time Enviro has to wake up to take a reading it will consume some of the available battery power. By selecting a longer time between readings you will substantially increase the length of time the batteries will last.

For most Enviro boards we recommend taking readings every fifteen minutes. This strikes a good balance between regular data points and a long (think months) battery life.

> The exception to the rule is Enviro Urban. Because it has to run a small fan to draw air across the particulate sensor it is a lot more power hungry than the other modules. We'd recommend only taking readings every hour or every three hours.

### Upload frequency

Your Enviro board will store the readings it takes locally and then upload a bunch of them all at once - this is much more power efficient than uploading every reading when it is taken.

Being connected to a wireless network consumes a lot of power so we want to avoid doing that as much as possible. There is some fixed overhead in starting up the wireless functionality so if we can just do that once for multiple readings it's much more efficient.

> The amount of power consumed when connected to a wireless network increases as the signal strength decreases so you may find, for example, that an Enviro installed outside seems to consume it's battery faster than one placed near the your network router indoors.

We recommend only uploading every five readings.

Click **Uploads ➔** to continue.

### Upload destination

Once Enviro is taking readings you'll probably want it to upload them to somewhere that you can view and analyse them. We support a number of destinations for your data:

- [**Adafruit IO**](#adafruit-io): A platform designed by our friends at Adafruit to store and display your data.
- [**MQTT**](#mqtt): The most commonly used messaging protocol for the Internet of Things (IoT).
- [**Custom HTTP endpoint**](#custom-http-endpoint): We'll make a request to your supplied URL with all of the data included.

#### Adafruit IO

Adafruit IO is a super simple way of getting started storing your data in the cloud, which lets you get up and going in minutes. It's really easy to set up a simple dashboard for viewing your sensor data. Adafruit offer a completely free tier which allows up to 10 feeds (for unlimited feeds it is $10/month or $99/year).

- [Adafruit IO](https://io.adafruit.com/)

Create an Adafruit IO account and take a copy of your user and access key (once logged in, you can find these by clicking on the key icon in the top menu bar).

> The access key is very long and you don't want to have to write it in by hand! We recommend you take a copy before you start the provisioning process so that you can copy and paste it into the field.

In your account create a new group called "enviro". Each sensor reading on your Enviro will automatically appear as a different feed named "[nickname]-[reading name]" (e.g. "weather-station-temperature", or "kitchen-humidity").

To set up a dashboard, with lovely graphs on it click on 'Dashboards' in the top menu bar and select 'Create new dashboard'. You can then click on the cog icon in the top right to create new blocks - we like line charts, but there's other options to choose from too! There's also an option to make your dashboard public if you want to share it with others.

#### MQTT

Want to post your data into a database or home automation system? MQTT is a commonly used protocol for doing that - to set it up you'll need the IP address or hostname of your MQTT broker, and a username and password.

The default topic that your broker needs to listen to is `enviro/board-nickname`

The default MQTT message will be a JSON dictionary that includes the timestamp of the reading, and the reading values.

#### Custom HTTP endpoint

If you're tech-savvy then you can use this option to process the data from Enviro yourself.

Simply provide a URL (with optional username and password) and your board will `POST` the readings to that endpoint.

The body of the `POST` will be a JSON dictionary that includes the timestamp of the reading, the nickname of the board, and the reading values. For example:

```json
{
  "nickname": "kitchen",
  "timestamp": "2022-08-02 15:32:10",
  "readings": {
    "temperature": 22.4,
    "humidity": 48.9,
    "pressure": 998.8,
    "lux": 87.3,
    "colour_temperature": 6840
  }
}
```

If your endpoint responds with a `200` status code then Enviro will delete it's local cached copy of these readings.

See the [Developer Guide](developer-guide.md) for more details.

Click **We're done! ➔** to continue.

### That's all folks!

That's it, we're ready to gather some readings! Place your Enviro in the location where you want it to do its work, hook up power, and perhaps give **POKE** a quick poke so that it can take its first reading - you should see the **ACTIVITY** LED light up briefly while it works.

After Enviro has taken enough readings to trigger an upload you'll start to see data appear in the service you selected.
