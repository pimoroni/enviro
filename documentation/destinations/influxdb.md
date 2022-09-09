# InfluxDB

InfluxDB is a special kind of database that is designed to store and analyse time-based data.

It's really simple to set up a simple dashboard for viewing your sensor data. InfluxDB offers a generous free tier which is rate limited (5MB of writes/5 mins) and will store your data for up to 30 days. There's also pay as you go plans if you need more.

They also offer a self-hosted option [InfluxDB Open Source](https://www.influxdata.com/products/editions/) which you can install on your own hardware.

## Setting up an InfluxDB Cloud account

1. Visit [InfluxDB](https://www.influxdata.com/get-influxdb/)
2. Create an account by clicking **Use It for Free**
3. Create your account using whichever login mechanism you prefer.
4. Go into your user settings (click on your email address at the top of the InfluxDB Cloud interface) and look at **Organisation Profile**.
5. Take note of your **Name** and **Cluster URL (Host Name)** you'll need these later.
6. Click on 'Load Data' in the sidebar and select 'Buckets'. Create a new **bucket** called `enviro`.
7. You'll also need to generate an **API token** using 'Load Data' > 'API tokens'. Make a custom API token with write access to the `enviro` bucket.

When you provision your device enter the name, cluster URL, API token and bucket name and Enviro will automatically start sending data on the schedule you have requested.

## Setting up your own local InfluxDB database

- To post Enviro data into a locally hosted InfluxDB you'll just need to enter the IP/hostname of your database in **URL** (e.g. http://influxdb.local:8086 or http://192.168.0.1:8086) and the name of your database (chosen during setup) in **bucket**. Organisation name and API token can be left blank.

View the list of sensor readings provided by each board: [Enviro Indoor](../boards/enviro-indoor.md), [Enviro Grow](../boards/enviro-grow.md), [Enviro Weather](../boards/enviro-weather.md), [Enviro Urban](../boards/enviro-urban.md).
