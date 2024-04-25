# Weather Underground

Referred to as "wunderground in config and code", Weather Underground is an online service provided by IBM for uploading and viewing information from personal Weather Stations (PWS) and provides general weather forecasts and news.

You can sign up for a free account, configure a device and drop the credentials into the Enviro configuration to have the values appear on your own weather station dashboard that is also shared with the world.

## Setting up a Weather Underground account and device

1. Visit [Weather Underground](https://www.wunderground.com/)
2. Create an account by clicking [Join](https://www.wunderground.com/signup) in the navigation bar
3. Create your account using your email and a new password
4. Browse to your [devices](https://www.wunderground.com/member/devices) in your profile
5. Click Add New Device - Select "Raspberry Pi" as the device hardware and follow the wizard selecting appropriate values (if in doubt, go American units)
6. Credentials are displayed on the summary screen, but you can check these at any time on the device page

When you provision your device enter the station ID and station key and Enviro will automatically start sending data on the schedule you have requested.

Ensure you have enabled the sea level pressure option and provided accurate [elevation data](https://whatismyelevation.com/) if you want to return pressure data.

You can view the dashboard for your station by clicking the station name on the [devices](https://www.wunderground.com/member/devices) page.

## Supported readings
The following readings will be uploaded. Depending on board type, other readings may be collected, but not sent to Weather Underground and essentially dropped.
- Temperature
- Humidity
- Sea level pressure
- Wind speed
- Wind direction

There is potential to build logic to calculate rain per hour and convert luminance to solar radiation to capture all Enviro Weather sensor output, other boards may not be well suited to this destination.