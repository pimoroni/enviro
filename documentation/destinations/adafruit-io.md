# Adafruit IO

Adafruit IO is a super simple way of getting started storing your data in the cloud, which lets you get up and going in minutes.

It's really easy to set up a simple dashboard for viewing your sensor data. Adafruit offer a completely free tier which allows up to 10 feeds or for unlimited feeds it is $10/month (or $99/year).

While Adafruit IO is a paid service we highly recommend it for its simplicity - it's also a great way to support the work Adafruit do!

## Setting up your Adafruit IO account

1. Visit [Adafruit IO](https://io.adafruit.com/)
2. Create an Adafruit account by clicking **Get Started for Free**
3. Click the key icon (API Key) in the menu at the top of the page
4. Take a copy of your **Username** and **Key** (see note below!)
5. Go to the **Feeds** page linked from the menu at the top of the page
6. Create a new group called `enviro`

> Note: the access key is **very long** and you don't want to have to write it in by hand! We recommend you take a copy before you start the provisioning process so that you can copy and paste it into the field when needed.

When you provision your device you'll enter the Username and Key that we created and Enviro will automatically start sending data on the schedule you have requested.

## How to access your data

Each sensor reading on your Enviro will automatically appear as a different feed within the group `enviro` named `[nickname]-[reading name]` once it starts uploading data (e.g. `weather-station-temperature`, or `kitchen-humidity`).

> You don't need to manually create the feeds for Enviro - it will happen automatically.

View the list of sensor readings provided by each board: [Enviro Indoor](../boards/enviro-indoor.md), [Enviro Grow](../boards/enviro-grow.md), [Enviro Weather](../boards/enviro-weather.md), [Enviro Urban](../boards/enviro-urban.md).

## How to view your data

To set up a dashboard, with lovely graphs on it click on 'Dashboards' in the top menu bar and select 'Create new dashboard'. You can then click on the cog icon in the top right to create new blocks - we like line charts, but there's other options to choose from too! There's also an option to make your dashboard public if you want to share it with others.