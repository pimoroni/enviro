# Weather Underground

Contracted to "wunderground in config and code" Weather Underground is a web service run by IBM for uploading and viewing information from personal Weather Stations (PWS).

You can sign up for a free acount, configure a device and drop the credentials into the Enviro configuration to have the values appear on your own weather station dashboard that is also shared with the world.

## Setting up a Weather Underground account and device

1. Visit [Weather Underground](https://www.wunderground.com/)
2. Create an account by clicking [Join](https://www.wunderground.com/signup) in the navigation bar.
3. Create your account using your email and a new password
4. Browse to your [devices](https://www.wunderground.com/member/devices) in your profile
5. Click Add New Device - Select Raspberry Pi as device hardware and follow the wizard selecting appropriate values (if in doubt, go American units)
6. Credentials are displayed on the summary screen, but you can check these at any time on the device page

When you provision your device enter the station ID and station key and Enviro will automatically start sending data on the schedule you have requested.

You can view the dashboard for your station by clicking the station name on the [devices](https://www.wunderground.com/member/devices) page.