# MQTT

[MQTT](https://mqtt.org/) (MQ Telemetry Transport) is a protocol designed to allow devices and servers to communicate with each other - it is used by many home automation and logging systems.

An MQTT broker accepts messages that are published to it by devices (such as garage door remote sensor) and holds onto those messages until a consumer (such as an automatic garage door opener) is ready to receive them. This allows both the device and the consumer to operate at their own pace without relying on each other to be able to respond immediately at all times. It is an essential layer in home automation and data gathering where many disparate devices and consumers are working together to create a larger system.

You may choose to run your own MQTT broker or use a cloud hosted one (though these generally have a small monthly cost associated).

## Setting up an MQTT broker

This is a great option for people who want to control their own data, avoid any monthly fees, and are comfortable running their own server.

We recommend [Mosquitto](https://mosquitto.org/) which is an open source and lightweight MQTT broker ideal for running on lower power devices like the Raspberry Pi. It is available for Windows, MacOS, and Linux.

Steve's Internet Guide has instructions for installing Mosquitto on both [Windows](http://www.steves-internet-guide.com/install-mosquitto-broker/) and [Linux](http://www.steves-internet-guide.com/install-mosquitto-linux/) which are worth checking out.

## Support for local SSL with MQTT Broker

1 > Upload the certificate file to your pico for example a file called ca.crt 

2 > Update the config.py file and add the line `mqtt_broker_ca_file = 'ca.crt'` replacing ca.crt with the path to the file

The mqtt.py destination file will attempt to use SSL if the `mqtt_broker_ca_file` is not none. 

## Using a cloud hosted MQTT broker

Alternatively you can avoid any software setup and having to manage your own server by using one of the many hosted MQTT broker services. These generally come with a small monthly fee (£3-5) or have very limited capabilities.

Some options worth looking at:

- [MYQTTHub](https://myqtthub.com/): £2/mo (also has free tier), 100 connections, max 100MB storage
- [CloudMQTT](https://www.cloudmqtt.com/): $5/mo, 25 connections, 20Kbit/s data rate
- [AWS IoT Core MQTT](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html): 

EMQ also provide a public MQTT broker for IoT testing https://www.emqx.com/en/mqtt/public-mqtt5-broker which can be useful just to check things are working while you're setting them up.

## Topic name and message format

Enviro boards will publish to a topic called `enviro/[nickname]` where `[nickname]` is the nickname you gave your board during provisioning.

Each message published has a JSON payload that includes the sensor readings along with some general information such as when the readings were taken, the board's nickname, and the model of the board.

```json
{
  "nickname": "weather-test", 
  "model": "grow",
  "uid": "e6614c775b8c4035", 
  "timestamp": "2022-09-04T10:40:24Z", 
  "readings": {
    "temperature": 27.57,   // will change depending on board model
    "humidity": 49.33, 
    "pressure": 996.22, 
    "light": 0.41, 
    "moisture_1": 0.0, 
    "moisture_2": 0.0, 
    "moisture_3": 0.0, 
    "voltage": 4.954
  }
}
```

View the list of sensor readings provided by each board: [Enviro Indoor](../boards/enviro-indoor.md), [Enviro Grow](../boards/enviro-grow.md), [Enviro Weather](../boards/enviro-weather.md), [Enviro Urban](../boards/enviro-urban.md).
