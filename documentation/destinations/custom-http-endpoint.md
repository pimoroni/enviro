# Custom HTTP Endpoint

If you're tech-savvy (or have too much spare time) then you can use this option to process the data from Enviro yourself - you can also use this functionality to integrate with services that accept data via webhooks like [IFTTT](https://ifttt.com/). 

## Implementing your HTTP endpoint

Your service will need to accept HTTP `POST` requests which include a JSON body that contains the sensor readings and other information.

Optionally you can provide a username and password for HTTP authorisation.

## Message format

The body of the `POST` request will be a JSON dictionary that includes the timestamp of the reading, the nickname of the board, and the reading values. For example:

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

If your endpoint responds with a `200`, `201`, or `202` status code then Enviro will delete it's local cached copy of these readings.