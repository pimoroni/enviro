# InfluxDB

InfluxDB is a special kind of database that is designed to store and analyse time-based data.

It's really simple to set up a simple dashboard for viewing your sensor data. InfluxDB offers a completely free tier which is rate limited and also a pay as you go plan if you need more.

They also offer a self-hosted option [InfluxDB Open Source](https://www.influxdata.com/products/editions/) which you can install on your own hardware.

## Setting up your InfluxDB account

1. Visit [InfluxDB](https://www.influxdata.com/get-influxdb/)
2. Create an account by clicking **Use It for Free**
3. Create your account using whichever login mechanism you prefer
4. Go into your user settings and look at **Organisation**
5. Take note of your **Name** and **Cluster URL (Host Name)** you'll need these later
6. Click on **Load Data** in the sidebar and select **Buckets**
7. Create a new bucket called `enviro`

When you provision your device you'll enter the Name, Cluster URL, and Token that we created and Enviro will automatically start sending data on the schedule you have requested.

View the list of sensor readings provided by each board: [Enviro Indoor](../boards/enviro-indoor.md), [Enviro Grow](../boards/enviro-grow.md), [Enviro Weather](../boards/enviro-weather.md), [Enviro Urban](../boards/enviro-urban.md).
